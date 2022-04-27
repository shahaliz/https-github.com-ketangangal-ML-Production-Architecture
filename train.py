from aws_feature_store.feature_store import FeatureStoreConnection
from aws_model_registry.model_registry import ModelRegistryConnection
from data_preprocessing_service.preprocessing import Preprocessing
from sklearn.metrics import accuracy_score, f1_score, recall_score
from email_notification_service.email_service import EmailSender
from sklearn.ensemble import RandomForestClassifier
from utils.utils import read_config
from from_root import from_root
from joblib import dump
import os


class TrainModel:
    def __init__(self):
        self.config = read_config()
        self.feature_store = self.config["feature_store"]["bucket_name"]
        self.raw_data_key = self.config["feature_store"]["file_name"]
        self.model_registry = self.config["model_registry"]["bucket_name"]
        self.label = None
        self.test_size = None
        self.random_state = None
        self.message = None
        self.zip_files = None
        self.package_name = None

    @staticmethod
    def model(X_train, X_test, y_train, y_test):
        # Model Initialization
        model = RandomForestClassifier(n_estimators=120)
        model.fit(X_train, y_train)

        # Prediction
        prob = model.predict_proba(X_test)[:, 1]

        # Metrics Calculation
        accuracy = accuracy_score(y_test, prob)
        f1 = f1_score(y_test, prob)
        recall = recall_score(y_test, prob)

        model_path = os.path.join(from_root(),"artifacts","model.pkl")
        dump(model,model_path)

        return accuracy, f1, recall

    def send_email(self):
        mail = EmailSender(sender_email=self.config,application_key=self.config,
                           receiver_email=self.config,message=self.message)
        mail.send_email()

    def train(self):
        feature_data = FeatureStoreConnection(bucket_name=self.feature_store,key=self.raw_data_key)
        raw_data = feature_data.get_features_from_s3()

        preprocess = Preprocessing(df=raw_data,label=self.label,test_size=self.test_size,random_state=self.random_state)
        X_train, X_test, y_train, y_test = preprocess.preprocess()

        accuracy, f1, recall = self.model(X_train, X_test, y_train, y_test)

        print(f"Accuracy : {accuracy}")
        print(f"f1_score : {f1}")
        print(f"recall_score : {recall}")

        registry = ModelRegistryConnection(bucket_name=self.model_registry,zip_files=self.zip_files,
                                           package_name=self.package_name)
        registry.upload_model_in_test()

        self.send_email()

        return "Process Completed"


if __name__ == "__main__":
    train_model = TrainModel()
    train_model.train()
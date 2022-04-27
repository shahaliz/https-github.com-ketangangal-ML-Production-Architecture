from aws_connection.service import FeatureStoreConnection
from aws_connection.service import ModelRegistryConnection
from data_preprocessing_service.preprocessing import Preprocessing
from email_notification_service.email_service import EmailSender

from sklearn.ensemble import RandomForestClassifier


def train_model():
    # Get Data from Feature Store
    feature_data = FeatureStoreConnection(bucket_name="featurestorek10", key="HeartDiseaseTrain-Test.csv")
    data = feature_data.get_features_from_s3()

    #  Preprocessing on Data
    preprocess = Preprocessing(data, "target", test_size=0.30, random_state=101)
    X_train, X_test, y_train, y_test = preprocess.preprocess()

    # Model Training
    model = RandomForestClassifier(n_estimators=120)
    model.fit(X_train, y_train)
    prob = model.predict_proba(X_test)[:, 1]
    #print("Prediction Results :",prob)

    # Store model pickle
    path = r"F:\Production\ML-Production-Architecture\model_training\artifacts\model.pkl"

    # Create Model pkl and upload to testing registry
    registry = ModelRegistryConnection("modelregistryk10", "model.pkl", "model.pkl")
    registry.upload_model_in_test(model,path)

    # Email Notification
    # sender_email = "ketangangal98@gmail.com"
    # receiver_email = "ketangangal98@gmail.com"
    # application_key =
    # message = "Model successfully registered"
    #
    # mail = EmailSender(sender_email, application_key, receiver_email, message)
    # mail.send_email()
    return "Process Completed"


if __name__ == "__main__":
    response = train_model()
    print(response)

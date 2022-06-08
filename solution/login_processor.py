import hashlib
import boto3
import os
import json
import database_handler

# For the constraints of this assessment, this function will run locally. Ideally, this function would run as a Lambda
# in the AWS account and be triggered when new messages are delivered to the SQS queue. Reference: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html


# The endpoint for our AWS environment. Needs to be set for interfacing with localstack in particular
ENDPOINT_URL = os.environ.get("ENDPOINT_URL", None)
# The SQS queue ARN
QUEUE_URL = os.environ["QUEUE_URL"]
# The full connection string URL for the postgres database. Refer to the README for format
DB_URL = os.environ["DB_URL"]


# Hash a particular value using SHA256
# In a real environment and if this data is sensitive enough, I'd recommend encrypting the hash with an encryption key stored in AWS Secrets Manager
# This is fine for a simple assessment though
def hashvalue(value: bytes):
    return hashlib.sha256(value).hexdigest()


# Simple wrapper function to return boto3 clients for different AWS services
# This could be extended into a function that handles different endpoint types as well, such as VPC or FIPS endpoints
def setup_client(service: str):
    if ENDPOINT_URL:
        return boto3.client(service, endpoint_url=ENDPOINT_URL)
    else:
        return boto3.client(service)


# Retrieve messages from the SQS queue, maximum of 10 messages per call and "hide" the messages from being reprocessed for 30 seconds
# Could use type annotations to declare strict typing via something like
def retrieve_messages(client):
    messages = client.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10, VisibilityTimeout=30)
    # Only return the messages if our response from SQS was a success. Otherwise raise an error
    if 200 <= messages["ResponseMetadata"]["HTTPStatusCode"] < 400:
        return messages["Messages"] if "Messages" in messages.keys() else []  # Return an empty list if we've processed all the messages
    else:
        raise ValueError(f"ERROR: Expected HTTP status code 200-300, got an error. "
                         f"Please check SQS client and environment configuration. "
                         f"Got status code {messages['ResponseMetadata']['HTTPStatusCode']}")


# Process the messages from our SQS queue by converting from string to JSON, hashing the device_id and ip,
# and formatting the key/value pairs so they match our user_logins table schema (see the database_handler.py script).
# Then use the database_handler object to insert the properly formatted values into the database
# Finally, deletes the SQS messages when done
def process_messages(messages: [str], db, client):
    login_list = list()
    processed_list = list()
    # Loop over each message in the message list, completing the operations listed in the above comment block
    for message in messages:
        login_data = json.loads(message["Body"])
        login_data["masked_device_id"] = hashvalue(login_data["device_id"].encode("utf-8"))
        login_data["masked_ip"] = hashvalue(login_data["ip"].encode("utf-8"))
        login_data["app_version"] = login_data["app_version"].replace(".", "") # Due to the Postgres table using an Integer data type, we must convert app_version from a x.y.z format to xyz
        login_data.pop("ip")
        login_data.pop("device_id")
        login_list.append(login_data)
        # The processed_list variable is just to store MessageIds and ReceiptHandles for deleting messages after processing
        # Not necessary if deploying via AWS Lambda
        processed_list.append({"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]})
    db.insert_logins(login_list)
    # Assuming our formatting and insertion into the DB succeeded, remove the processed messages from the queue so they don't get reprocessed
    # Note this would not be necessary if deploying onto AWS Lambda with an SQS trigger, since Lambda will automatically clear the processed messages when finished (assuming no errors occurred)
    delete_response = client.delete_message_batch(
        QueueUrl=QUEUE_URL,
        Entries=processed_list
    )
    if "Failed" in delete_response.keys():
        # This error message could be more descriptive
        raise ValueError("ERROR: Detected failed deletions in the process_messages script.")


if __name__ == "__main__":
    # Instantiate a boto3 client object for SQS and a database handler (refer to the database_handler.py script)
    sqs_client = setup_client("sqs")
    db_handler = database_handler.UserDatabaseHandler(db_url=DB_URL)
    # Retrieve the raw message list from SQS
    raw_messages = retrieve_messages(sqs_client)
    # Continue querying the SQS queue until we've processed all the messages
    # This is only required for local runs-- if this were deployed to a serverless AWS service like Lambda or Fargate, this would be unnecessary
    while len(raw_messages) > 0:
        print("... processing batch ...")
        process_messages(raw_messages, db_handler, sqs_client)
        raw_messages = retrieve_messages(sqs_client)
    print(">>> Done!")

import json

import boto3
from botocore.exceptions import ClientError

from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    ENDPOINT_URL,
    QUEUE_NAME,
    BUCKET_NAME,
)

def get_aws_client(service):

    client = boto3.client(
        service,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        endpoint_url=ENDPOINT_URL
    )

    return client

def list_buckets():
    
    s3      = get_aws_client("s3")
    buckets = s3.list_buckets().get("Buckets", [])
    
    return buckets

def upload_file_to_bucket(file_obj, filename: str):

    s3 = get_aws_client("s3")
    
    try:
        s3.upload_fileobj(file_obj, BUCKET_NAME, filename)
        return True
    
    except ClientError as e:
        print(f"error sending to bucket: {e}")
        return False

def get_queue_url():

    sqs      = get_aws_client("sqs")
    response = sqs.get_queue_url(QueueName=QUEUE_NAME)
    
    return response["QueueUrl"]

def send_message_to_queue(message: dict):
    
    sqs         = get_aws_client("sqs")
    queue_url   = get_queue_url()

    response    = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )

    return response


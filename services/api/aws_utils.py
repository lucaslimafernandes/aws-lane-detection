import boto3
from botocore.exceptions import ClientError

from settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_ENDPOINT_URL,
)

def get_s3_client():

    client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        endpoint_url=S3_ENDPOINT_URL
    )

    return client

def list_buckets():
    
    s3      = get_s3_client()
    buckets = s3.list_buckets().get("Buckets", [])
    
    return buckets

def upload_file_to_bucket(bucket_name: str, file_obj, filename: str):

    s3 = get_s3_client()
    
    try:
        s3.upload_fileobj(file_obj, bucket_name, filename)
        return True
    
    except ClientError as e:
        print(f"error sending to bucket: {e}")
        return False


import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_REGION              = os.getenv("AWS_REGION", "us-east-1")
ENDPOINT_URL            = os.getenv("AWS_ENDPOINT_URL", None)

QUEUE_NAME              = os.getenv("SQS_QUEUE_NAME", "queue1")
BUCKET_NAME             = os.getenv("S3_BUCKET_NAME", "bucket1")

EXT_FILES               = (".mp4", ".mov", ".avi", ".mkv")


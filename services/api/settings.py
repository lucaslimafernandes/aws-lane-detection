import os

USE_LOCALSTACK = os.getenv("USE_LOCALSTACK", "true").lower() == "true"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

S3_ENDPOINT_URL = (
    "http://localhost:4566" if USE_LOCALSTACK else None
)

EXT_FILES = (".mp4", ".mov", ".avi", ".mkv")


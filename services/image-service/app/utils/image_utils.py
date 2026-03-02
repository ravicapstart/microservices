import boto3
import os
from io import BytesIO

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET = os.getenv("AWS_BUCKET_NAME")

def download_from_s3(key):
    print("BUCKET VALUE:", BUCKET)
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return obj["Body"].read()


def upload_to_s3(file_bytes, key):
    s3.put_object(Bucket=BUCKET, Key=key, Body=file_bytes)
    return f"https://{BUCKET}.s3.amazonaws.com/{key}"
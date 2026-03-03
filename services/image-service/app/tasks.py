from .celery_app import celery_app
from .utils.image_utils import download_from_s3, upload_to_s3
from PIL import Image
from io import BytesIO
import uuid
from celery import Celery
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "worker",
    broker=os.getenv("BROKER_URL")
)
celery.conf.task_default_queue = "image_queue"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

SIZES = {
    "thumbnail": (200, 200),
    "small": (400, 400),
    "large": (800, 800),
}


@celery.task(name="resize_image")
def resize_image(payload: dict):

    image_id = payload["image_id"]
    s3_key = payload["s3_key"]
    
    bucket = os.getenv("AWS_BUCKET_NAME")

    obj = s3.get_object(Bucket=bucket, Key=s3_key)
    img = Image.open(io.BytesIO(obj["Body"].read()))

    generated_urls = {}

    for size_name, size in SIZES.items():
        img_copy = img.copy()
        img_copy.thumbnail(size)

        buf = io.BytesIO()
        img_copy.save(buf, format="JPEG")
        buf.seek(0)

        new_key = f"properties/{size_name}/{image_id}.jpg"

        s3.put_object(
            Bucket=bucket,
            Key=new_key,
            Body=buf,
            ContentType="image/jpeg"
        )

        generated_urls[size_name] = f"https://{bucket}.s3.amazonaws.com/{new_key}"

    # send callback to Django
    requests.post(payload["callback_url"], json={
        "image_id": image_id,
        **generated_urls
    })

    return {"status": "done"}
    
    
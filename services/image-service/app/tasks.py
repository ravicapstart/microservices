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

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)


def process_property_image(image_id):
    image_obj = PropertyImage.objects.get(id=image_id)
    
    # Download image from S3
    obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=image_obj.image.name)
    img = Image.open(io.BytesIO(obj['Body'].read()))
    
    generated_urls = {}

    # Resize and upload each size
    for size_name, size in SIZES.items():
        img_copy = img.copy()
        img_copy.thumbnail(size)
        buf = io.BytesIO()
        img_copy.save(buf, format="JPEG")
        buf.seek(0)
        new_key =  f"properties/{size_name}/{image_obj.id}.jpg"
        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=new_key, Body=buf, ContentType="image/jpeg")
        
          # ✅ Build URL
        generated_urls[size_name] = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{new_key}"

    # ✅ SAVE TO DATABASE
    image_obj.thumbnail_url = generated_urls.get("thumbnail")
    image_obj.small_url = generated_urls.get("small")
    image_obj.large_url = generated_urls.get("large")

    image_obj.save()
    
    
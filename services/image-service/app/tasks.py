from .celery_app import celery_app
from .utils.image_utils import download_from_s3, upload_to_s3
from PIL import Image
from io import BytesIO
import uuid
from celery import Celery

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


SIZES = {
    "thumbnail": (200, 200),
    "small": (400, 400),
    "large": (800, 800),
}


@celery.task(name="process_property_image")
def resize_image(payload):
    """
    payload example:
    {
        "image_id": 12,
        "s3_key": "properties/original/abc.jpg",
        "width": 800,
        "height": 600,
        "callback_url": "http://100.27.62.33:8001/api/update-image/"
    }
    """

    image_id = payload["image_id"]
    s3_key = payload["s3_key"]
    callback_url = payload["callback_url"]
    bucket_name = os.getenv("AWS_BUCKET_NAME")

    # 1️⃣ Download original image
    obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
    img = Image.open(io.BytesIO(obj["Body"].read()))

    generated_urls = {}

    # 2️⃣ Resize & upload
    for size_name, size in SIZES.items():
        img_copy = img.copy()
        img_copy.thumbnail(size)

        buf = io.BytesIO()
        img_copy.save(buf, format="JPEG")
        buf.seek(0)

        new_key = f"properties/{size_name}/{image_id}.jpg"

        s3.put_object(
            Bucket=bucket_name,
            Key=new_key,
            Body=buf,
            ContentType="image/jpeg"
        )

        generated_urls[size_name] = (
            f"https://{bucket_name}.s3.amazonaws.com/{new_key}"
        )

    # 3️⃣ Send results back to Django
    requests.post(callback_url, json={
        "image_id": image_id,
        "thumbnail_url": generated_urls.get("thumbnail"),
        "small_url": generated_urls.get("small"),
        "large_url": generated_urls.get("large"),
    })

    return {"status": "success", "image_id": image_id}



@celery_app.task(name="app.tasks.resize_image")
# def resize_image(s3_key, width, height):

#     # Download image from S3
#     image_bytes = download_from_s3(s3_key)

#     # Open image
#     img = Image.open(BytesIO(image_bytes))

#     # Resize
#     img = img.resize((width, height))

#     # Save to memory
#     buffer = BytesIO()
#     img.save(buffer, format="JPEG")
#     buffer.seek(0)

#     # New S3 key
#     new_key = f"properties/resized/{width}x{height}_{s3_key}"

#     # Upload back to S3
#     new_url = upload_to_s3(buffer.getvalue(), new_key)
#     return new_url
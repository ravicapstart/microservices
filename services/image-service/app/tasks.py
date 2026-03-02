from .celery_app import celery_app
from .utils.image_utils import download_from_s3, upload_to_s3
from PIL import Image
from io import BytesIO
import uuid

@celery_app.task(name="app.tasks.resize_image")
def resize_image(s3_key, width, height):

    # Download image from S3
    image_bytes = download_from_s3(s3_key)

    # Open image
    img = Image.open(BytesIO(image_bytes))

    # Resize
    img = img.resize((width, height))

    # Save to memory
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    # New S3 key
    new_key = f"properties/resized/{width}x{height}_{s3_key}"

    # Upload back to S3
    new_url = upload_to_s3(buffer.getvalue(), new_key)
    return new_url
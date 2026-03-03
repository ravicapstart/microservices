from fastapi import FastAPI
from .tasks import resize_image, resize_image

app = FastAPI()

@app.post("/resize")
def resize(payload : dict, width: int = 300, height: int = 300):
    
    # payload = {
    #     "image_id": 1,
    #     "s3_key": "properties/original/test.jpg",
    #     "width": 800,
    #     "height": 600,
    #     "callback_url": "http://your-django-ip:8000/api/update-image/"
    # }
    
    task = resize_image.delay(payload)
    return {"task_id": task.id}

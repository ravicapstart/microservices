from fastapi import FastAPI
from .tasks import resize_image

app = FastAPI()

@app.post("/resize")
def resize(payload : dict, width: int = 300, height: int = 300):
    
#    {
#     "image_id": 12,
#     "s3_key": "properties/original/test.jpg",
#     "callback_url": "http://django-ip/api/update-image/"
#     }
    
    task = resize_image.delay(payload)
    return {"task_id": task.id}

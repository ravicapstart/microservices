from fastapi import FastAPI
from .tasks import resize_image

app = FastAPI()

@app.post("/resize")
def resize(s3_key: str, width: int = 300, height: int = 300):
    task = resize_image.delay(s3_key, width, height)
    print("task",task)
    return {"task_id": task.id}

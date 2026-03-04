from dotenv import load_dotenv
load_dotenv()

from celery import Celery
from .config import RABBITMQ_URL


celery_app = Celery(
    "image_service",
    broker=RABBITMQ_URL,
    #backend=REDIS_URL
)

celery_app.conf.task_routes = {
    "app.tasks.resize_image": {"queue": "image_queue"},
}


celery_app.autodiscover_tasks(["app"])
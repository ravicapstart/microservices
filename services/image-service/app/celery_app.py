from dotenv import load_dotenv
load_dotenv()

from celery import Celery

celery_app = Celery(
    "image_service",
    broker=f"amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASS')}@{os.getenv('RABBITMQ_HOST')}:5672//",
    #backend=REDIS_URL
)

celery_app.conf.task_routes = {
    "resize_image": {"queue": "image_queue"},
}


celery_app.autodiscover_tasks(["app"])
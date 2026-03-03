import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
#RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672//"
RABBITMQ_URL = "amqp://akshit:akshit@2026@100.27.62.33:5672//"
#REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")u 
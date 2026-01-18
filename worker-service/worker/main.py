import os
import json
import time
import pika
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import ImageJob, ImageVariant
from .storage import get_original, put_thumbnail
from .image_processor import make_thumbnail

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE = "image-jobs"


def process_job(payload: dict):
    job_id = payload["job_id"]
    original_key = payload["original_key"]

    db: Session = SessionLocal()
    try:
        job = db.query(ImageJob).filter(ImageJob.id == job_id).first()
        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        original = get_original(original_key)
        thumbnail = make_thumbnail(original)

        thumb_key = f"{job_id}_thumb.jpg"
        put_thumbnail(thumb_key, thumbnail)

        variant = ImageVariant(
            job_id=job_id,
            type="thumbnail",
            object_key=thumb_key,
        )
        db.add(variant)

        job.status = "DONE"
        db.commit()

    except Exception as e:
        job = db.query(ImageJob).filter(ImageJob.id == job_id).first()
        if job:
            job.status = "FAILED"
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()


def on_message(ch, method, properties, body):
    payload = json.loads(body)
    process_job(payload)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def connect_with_retry():
    params = pika.URLParameters(RABBITMQ_URL)

    for attempt in range(1, 31):
        try:
            return pika.BlockingConnection(params)
        except Exception as e:
            print(f"RabbitMQ not ready (attempt {attempt}/30): {e}")
            time.sleep(2)

    raise RuntimeError("Could not connect to RabbitMQ after 30 attempts")


def main():
    connection = connect_with_retry()
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)

    print("Worker running. Waiting for jobs...")
    channel.start_consuming()


if __name__ == "__main__":
    main()

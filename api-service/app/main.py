from fastapi import FastAPI, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .db import engine, SessionLocal
from .models import Base, ImageJob
from .storage import put_original, presigned_original_url, presigned_thumbnail_url
from .rabbitmq import publish_job

app = FastAPI(title="Cloud-Native Image Processing API")

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/")
def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    return SessionLocal()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/images")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    job_id = str(uuid4())
    object_key = job_id
    data = await file.read()

    db = get_db()
    try:
        job = ImageJob(id=job_id, status="PENDING", original_key=object_key)
        db.add(job)
        db.commit()

        put_original(object_key=object_key, data=data, content_type=file.content_type)
        publish_job(job_id=job_id, original_key=object_key)

        return {"id": job_id, "status": "PENDING"}
    finally:
        db.close()

@app.get("/api/v1/images/{job_id}")
def get_job(job_id: str):
    db = get_db()
    try:
        job = db.query(ImageJob).filter(ImageJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        variants = []

        # original URL
        if job.original_key:
            variants.append({
                "type": "original",
                "url": presigned_original_url(job.original_key),
            })

        # thumbnail URL(s)
        for v in job.variants:
            if v.type == "thumbnail":
                variants.append({
                    "type": "thumbnail",
                    "url": presigned_thumbnail_url(v.object_key),
                })

        return {
            "id": job.id,
            "status": job.status,
            "error_message": job.error_message,
            "variants": variants,
        }
    finally:
        db.close()

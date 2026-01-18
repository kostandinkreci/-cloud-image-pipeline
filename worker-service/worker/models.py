from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from datetime import datetime
import uuid

Base = declarative_base()

def gen_uuid() -> str:
    return str(uuid.uuid4())

class ImageJob(Base):
    __tablename__ = "image_jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    status = Column(String)
    original_key = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    variants = relationship("ImageVariant", back_populates="job")

class ImageVariant(Base):
    __tablename__ = "image_variants"

    id = Column(String, primary_key=True, default=gen_uuid)
    job_id = Column(String, ForeignKey("image_jobs.id"))
    type = Column(String)
    object_key = Column(String)

    job = relationship("ImageJob", back_populates="variants")

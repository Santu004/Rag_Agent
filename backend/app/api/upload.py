from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.rag.vectorstore import process_pdf_and_store

router = APIRouter(prefix="/upload", tags=["Upload"])


class UploadRequest(BaseModel):
    file_path: str


@router.post("/")
def upload_pdf(payload: UploadRequest):
    try:
        process_pdf_and_store(payload.file_path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

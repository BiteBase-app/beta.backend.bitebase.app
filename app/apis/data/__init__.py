from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

router = APIRouter(prefix="/data_integration", tags=["data_integration"])

class DataSource(BaseModel):
    id: str
    name: str
    type: str
    icon: str
    status: str
    lastSync: Optional[str] = None

class DataSourceList(BaseModel):
    sources: List[DataSource]

# Sample data sources
DATA_SOURCES = [
    {
        "id": "1",
        "name": "POS System",
        "type": "integration",
        "icon": "cash-register",
        "status": "connected",
        "lastSync": "Today, 11:15 AM"
    },
    {
        "id": "2",
        "name": "Reservation System",
        "type": "integration",
        "icon": "calendar-check",
        "status": "connected",
        "lastSync": "Today, 10:30 AM"
    },
    {
        "id": "3",
        "name": "Delivery Platform",
        "type": "integration",
        "icon": "truck",
        "status": "connected",
        "lastSync": "Yesterday, 5:45 PM"
    },
    {
        "id": "4",
        "name": "Customer Feedback",
        "type": "integration",
        "icon": "comment-dots",
        "status": "disconnected"
    },
    {
        "id": "5",
        "name": "Excel",
        "type": "file",
        "icon": "file-excel",
        "status": "disconnected"
    },
    {
        "id": "6",
        "name": "CSV",
        "type": "file",
        "icon": "file-csv",
        "status": "disconnected"
    },
    {
        "id": "7",
        "name": "Google Sheets",
        "type": "file",
        "icon": "table",
        "status": "disconnected"
    }
]

class FileUpload(BaseModel):
    id: str
    filename: str
    size: int
    uploadDate: str
    status: str
    type: str

# Sample file uploads
FILE_UPLOADS = []

@router.get("/sources")
async def get_data_sources() -> DataSourceList:
    """
    Get all data sources
    """
    return {"sources": DATA_SOURCES}

@router.get("/sources/{source_id}")
async def get_data_source(source_id: str) -> DataSource:
    """
    Get a data source by ID
    """
    for source in DATA_SOURCES:
        if source["id"] == source_id:
            return source
    
    raise HTTPException(status_code=404, detail="Data source not found")

@router.post("/sources/{source_id}/connect")
async def connect_data_source(source_id: str) -> DataSource:
    """
    Connect to a data source
    """
    for i, source in enumerate(DATA_SOURCES):
        if source["id"] == source_id:
            DATA_SOURCES[i]["status"] = "connected"
            DATA_SOURCES[i]["lastSync"] = "Just now"
            return DATA_SOURCES[i]
    
    raise HTTPException(status_code=404, detail="Data source not found")

@router.post("/sources/{source_id}/disconnect")
async def disconnect_data_source(source_id: str) -> DataSource:
    """
    Disconnect from a data source
    """
    for i, source in enumerate(DATA_SOURCES):
        if source["id"] == source_id:
            DATA_SOURCES[i]["status"] = "disconnected"
            DATA_SOURCES[i].pop("lastSync", None)
            return DATA_SOURCES[i]
    
    raise HTTPException(status_code=404, detail="Data source not found")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> FileUpload:
    """
    Upload a file
    """
    # In a real implementation, this would save the file to disk or cloud storage
    # For now, we'll just return a mock response
    
    file_id = str(len(FILE_UPLOADS) + 1)
    
    file_upload = {
        "id": file_id,
        "filename": file.filename,
        "size": 0,  # In a real implementation, this would be the actual file size
        "uploadDate": "2025-04-05",
        "status": "processed",
        "type": file.filename.split(".")[-1] if file.filename else "unknown"
    }
    
    # In a real implementation, we would add this to the database
    # FILE_UPLOADS.append(file_upload)
    
    return file_upload

@router.get("/uploads")
async def get_file_uploads() -> List[FileUpload]:
    """
    Get all file uploads
    """
    return FILE_UPLOADS

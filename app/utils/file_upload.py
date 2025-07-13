import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from app.config import settings

def save_uploaded_file(upload_file: UploadFile, folder: str = "prescriptions") -> str:
    """Save uploaded file and return the file path."""
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate file type
    if not upload_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = upload_file.file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large")
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Return relative path for database storage
    return str(file_path.relative_to(Path(settings.UPLOAD_DIR)))

def validate_image_file(upload_file: UploadFile) -> bool:
    """Validate that the uploaded file is a valid image."""
    try:
        # Read image data
        content = upload_file.file.read()
        upload_file.file.seek(0)  # Reset file pointer
        
        # Try to open with PIL
        image = Image.open(io.BytesIO(content))
        image.verify()
        return True
    except Exception:
        return False

def get_file_url(file_path: str) -> str:
    """Generate a URL for the uploaded file."""
    return f"/uploads/{file_path}" 
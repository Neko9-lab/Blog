from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pathlib import Path
import time

from app.core.deps import get_current_user
from app.models.user import User
from app.utils.response import success


router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[4] / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    _user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image upload allowed")

    suffix = Path(file.filename).suffix or ".png"
    filename = f"{int(time.time())}_{file.filename}"
    save_path = UPLOAD_DIR / filename

    content = await file.read()
    save_path.write_bytes(content)

    return success({"url": f"/static/uploads/{filename}"})

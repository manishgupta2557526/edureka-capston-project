from pathlib import Path
from typing import List
import os
import shutil

from app.config import ensure_data_dir, load_settings


class UploadService:
    def __init__(self, storage_dir: str | None = None) -> None:
        settings = load_settings()
        self.storage_dir = storage_dir or settings.upload_dir
        ensure_data_dir(self.storage_dir)

    def save_upload(self, uploaded_file, filename: str) -> str:
        safe_name = Path(filename).name
        destination = Path(self.storage_dir) / safe_name
        with open(destination, "wb") as handle:
            source = getattr(uploaded_file, "file", uploaded_file)
            if hasattr(source, "seek"):
                source.seek(0)
            shutil.copyfileobj(source, handle)
        return str(destination)

    def list_files(self) -> List[str]:
        return [path.name for path in Path(self.storage_dir).glob("*") if path.is_file()]

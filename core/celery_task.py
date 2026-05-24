from celery import shared_task
from django.core.files.storage import default_storage
from core.media_engine import upload_media


def _cleanup(temp_storage_path: str):
    """Delete the temp file from storage. Safe to call multiple times."""
    try:
        if default_storage.exists(temp_storage_path):
            default_storage.delete(temp_storage_path)
    except Exception as e:
        print(f"Warning: could not delete temp file {temp_storage_path}: {e}")


@shared_task(bind=True, max_retries=2)
def process_media_task(self, temp_storage_path: str):
    """
    Background task: compress + upload to Cloudinary, return URL.
    
    Cleanup rules:
      - SUCCESS  → delete temp file ✓
      - RETRY    → keep temp file so retry can use it ✓  
      - FAILURE  → delete temp file (no more retries) ✓
    """
    abs_path = default_storage.path(temp_storage_path)

    try:
        result = upload_media(abs_path)   
        _cleanup(temp_storage_path)

        return {
            "status": "done",
            "url":    result["url"],
            "type":   result["type"],
        }

    except Exception as exc:
        is_final_attempt = self.request.retries >= self.max_retries

        if is_final_attempt:
            _cleanup(temp_storage_path)
            raise  
        print(f"Task failed (attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}")
        raise self.retry(exc=exc, countdown=5)   
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

LOCAL_SESS_DIR = os.path.abspath("./local_data/sessions")
LOCAL_REPORTS_DIR = os.path.abspath("./local_data/reports")

os.makedirs(LOCAL_SESS_DIR, exist_ok=True)
os.makedirs(LOCAL_REPORTS_DIR, exist_ok=True)


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S.%fZ")


# Local-first storage
class LocalStorage:
    def __init__(self) -> None:
        self.sessions_dir = LOCAL_SESS_DIR
        self.reports_dir = LOCAL_REPORTS_DIR

    def save_session(self, session_id: str, data: Dict[str, Any]) -> str:
        path = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(self.sessions_dir, f"{session_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_sessions(self) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for fname in os.listdir(self.sessions_dir):
            if fname.endswith(".json"):
                sid = fname[:-5]
                results[sid] = os.path.join(self.sessions_dir, fname)
        return results

    def save_report(self, basename: str, content_bytes: bytes) -> str:
        safe = basename.replace("/", "_")
        path = os.path.join(self.reports_dir, f"{safe}-{_timestamp()}.pdf")
        with open(path, "wb") as f:
            f.write(content_bytes)
        return path


# Cloud stubs (disabled by default)
class AzureBlobStorageStub:
    def __init__(self) -> None:
        self.enabled = os.getenv("AZURE_BLOB_ENABLED", "false").lower() == "true"
        # Intentionally do not fail if credentials missing

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.enabled:
            return
        # Add actual implementation in cloud hand-off. Stub now.
        return


class S3StorageStub:
    def __init__(self) -> None:
        self.enabled = os.getenv("AWS_S3_ENABLED", "false").lower() == "true"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.enabled:
            return
        # Add actual implementation in cloud hand-off. Stub now.
        return


def get_storage():
    # Local-first
    return LocalStorage()
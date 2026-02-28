import sys
from pathlib import Path

# Ensure 'backend/' is on sys.path so `from app.xxx` imports work
# regardless of whether uvicorn is launched from project root or backend/
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

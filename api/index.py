import os
from pathlib import Path
# Vercel serverless filesystem is ephemeral. Keep temporary uploads under /tmp.
os.environ.setdefault("TALALTAM_DATA_DIR", "/tmp/talaltam")
os.environ.setdefault("UPLOAD_DIR", "/tmp/talaltam/uploads")
from server.app.main import app

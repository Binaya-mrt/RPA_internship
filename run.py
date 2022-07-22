import os
from app.main import app, VIDEO_UPLOAD_DIR
from uvicorn import run

if __name__ == "__main__":
    if not os.path.exists(VIDEO_UPLOAD_DIR):
        os.mkdir(VIDEO_UPLOAD_DIR)
    run(app, debug=True)

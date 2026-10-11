from pathlib import Path
import os


APP_NAME = "ESTELEICAO"


def get_user_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        base = Path(local_app_data)
    else:
        base = Path.home()

    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)

    return app_dir


USER_DIR = get_user_data_dir()

DATA_DIR = USER_DIR / "dados"
CACHE_DIR = USER_DIR / "cache"
LOG_DIR = USER_DIR / "logs"

for directory in (DATA_DIR, CACHE_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

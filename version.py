from pathlib import Path


def get_version() -> str:
    version_file = Path(__file__).resolve().parent / "VERSION"

    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


__version__ = get_version()

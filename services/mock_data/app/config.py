from pathlib import Path
import os


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(os.getenv("DATA_DIR", REPO_ROOT / "data"))

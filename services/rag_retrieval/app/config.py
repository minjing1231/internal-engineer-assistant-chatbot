from pathlib import Path
import os


REPO_ROOT = Path(__file__).resolve().parents[3]
SOP_FILE_PATH = Path(os.getenv("SOP_FILE_PATH", REPO_ROOT / "document" / "SOP.md"))
DEFAULT_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))

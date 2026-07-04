from pathlib import Path
import os


SOP_FILE_PATH = Path(os.getenv("SOP_FILE_PATH", "document/SOP.md"))
DEFAULT_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))

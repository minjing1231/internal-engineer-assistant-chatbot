import os


RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8001").rstrip("/")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8002").rstrip("/")
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:8003").rstrip("/")
SERVICE_TIMEOUT_SECONDS = float(os.getenv("SERVICE_TIMEOUT_SECONDS", "10"))

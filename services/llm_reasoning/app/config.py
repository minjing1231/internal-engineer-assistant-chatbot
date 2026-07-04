import os


LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://host.docker.internal:8080/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "LiquidAI/LFM2.5-1.2B-Instruct")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

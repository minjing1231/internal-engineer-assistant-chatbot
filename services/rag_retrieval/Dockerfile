FROM python:3.12-slim

WORKDIR /app

COPY services/rag_retrieval/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/rag_retrieval/app /app/app
COPY document /app/document

ENV SOP_FILE_PATH=/app/document/SOP.md

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

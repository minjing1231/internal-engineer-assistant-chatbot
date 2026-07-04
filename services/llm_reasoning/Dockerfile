FROM python:3.12-slim

WORKDIR /app

COPY services/llm_reasoning/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/llm_reasoning/app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

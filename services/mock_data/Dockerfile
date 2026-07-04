FROM python:3.12-slim

WORKDIR /app

COPY services/mock_data/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/mock_data/app /app/app
COPY data /app/data

ENV DATA_DIR=/app/data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]

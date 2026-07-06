# Deployment Guide

This guide explains how to run the Manufacturing Equipment Repair Engineer Chatbot on macOS or Windows when the user does not already have the model installed locally.

The application has two parts:

1. FastAPI microservices running through Docker Compose.
2. A local or remote OpenAI-compatible model server for the configured LLM.

The FastAPI services can run on macOS or Windows. The recommended local model path on macOS uses MLX. The recommended local model path on Windows uses Ollama because Ollama exposes an OpenAI-compatible `/v1` API that this project can call.

## 1. Prerequisites

### Required for All Users

- Git
- Docker Desktop
- Internet access for first-time Docker image and model downloads

### Required for Local MLX Model on Mac

- Apple Silicon Mac
- Python 3.11 or newer
- `pip3`

### Windows Model Note

MLX is not the recommended runtime on Windows. On Windows, use one of these options:

- Run the model through Ollama and configure `LLM_BASE_URL=http://host.docker.internal:11434/v1`.
- Run the app without a model and rely on deterministic fallback for demo purposes.
- Use a remote Mac/Linux machine exposing an OpenAI-compatible `/v1/chat/completions` endpoint.

## 2. Clone the Repository

```bash
git clone <your-repository-url>
cd internal-engineer-assistant-chatbot
```

Create the environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## 3. macOS Deployment with Local MLX Model

Use this path if the reviewer has an Apple Silicon Mac and wants to run `LiquidAI/LFM2.5-1.2B-Instruct` locally.

### 3.1 Install MLX Runtime

Create a virtual environment outside Docker:

```bash
python3 -m venv .mlx-venv
source .mlx-venv/bin/activate
pip install --upgrade pip
pip install mlx-lm
```

### 3.2 Start the Model Server

Run this in a separate terminal:

```bash
source .mlx-venv/bin/activate
python3 -m mlx_lm.server \
  --model LiquidAI/LFM2.5-1.2B-Instruct \
  --host 0.0.0.0 \
  --port 8080
```

The first run downloads the model, so it may take time.

Verify the model server:

```bash
curl http://localhost:8080/v1/models
```

### 3.3 Configure `.env`

For Docker Compose on Mac, keep:

```text
LLM_BASE_URL=http://host.docker.internal:8080/v1
LLM_MODEL=LiquidAI/LFM2.5-1.2B-Instruct
LLM_API_KEY=
LLM_TIMEOUT_SECONDS=30
SERVICE_TIMEOUT_SECONDS=45
```

`host.docker.internal` lets the Docker containers reach the model server running on the Mac host.

### 3.4 Start the Services

Run this in the project root:

```bash
docker compose up --build
```

Open the app:

```text
http://localhost:8000/
```

Demo login:

```text
Username: hana
Password: 123
```

## 4. Windows Deployment with Ollama

Use this path if the reviewer is on Windows and does not have MLX available.

### 4.1 Install Ollama

Install Ollama for Windows from:

```text
https://ollama.com/download
```

After installation, verify Ollama is running:

```powershell
curl.exe http://localhost:11434/api/tags
```

### 4.2 Prepare a Model in Ollama

This project is configured for `LiquidAI/LFM2.5-1.2B-Instruct`, but exact Ollama model availability can depend on what model tags or GGUF files are available to the reviewer.

Use one of the following approaches.

#### Option A: Pull an Existing Ollama Model Tag

If an Ollama tag for the desired model is available, pull it:

```powershell
ollama pull <ollama-model-name>
```

Then set `.env`:

```text
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_MODEL=<ollama-model-name>
LLM_API_KEY=ollama
LLM_TIMEOUT_SECONDS=30
SERVICE_TIMEOUT_SECONDS=45
```

For example, if the model is available locally under this name:

```text
LLM_MODEL=lfm2.5-1.2b-instruct
```

#### Option B: Import a GGUF Model into Ollama

If the reviewer has a GGUF file for the LiquidAI model, create a `Modelfile`:

```text
FROM C:\models\lfm2.5-1.2b-instruct.gguf
PARAMETER temperature 0.2
```

Create the Ollama model:

```powershell
ollama create lfm2.5-1.2b-instruct -f Modelfile
```

Then set `.env`:

```text
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_MODEL=lfm2.5-1.2b-instruct
LLM_API_KEY=ollama
LLM_TIMEOUT_SECONDS=30
SERVICE_TIMEOUT_SECONDS=45
```

#### Option C: Use a Different Ollama Demo Model

If the exact LiquidAI model is not available in Ollama, the services can still be demonstrated with another Ollama model that supports instruction following. Update only `LLM_MODEL` to the local Ollama model name.

This changes the demo model, so mention it during the walkthrough.

### 4.3 Verify Ollama OpenAI Compatibility

Ollama exposes an OpenAI-compatible endpoint at:

```text
http://localhost:11434/v1
```

Verify models:

```powershell
curl.exe http://localhost:11434/v1/models
```

Test chat completions:

```powershell
curl.exe http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"lfm2.5-1.2b-instruct\",\"messages\":[{\"role\":\"user\",\"content\":\"Return JSON only: {\\\"ok\\\": true}\"}]}"
```

Replace `lfm2.5-1.2b-instruct` with the actual local Ollama model name.

### 4.4 Start FastAPI Services

Create `.env`:

```powershell
Copy-Item .env.example .env
```

Then start Docker Compose:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8000/
```

Demo login:

```text
Username: hana
Password: 123
```

### 4.5 Fallback Option: Run Without a Local Model

If no model endpoint is available, the application still runs.

Expected behavior:

- RAG Retrieval Service retrieves SOP chunks.
- Mock Data Service returns equipment, alarm, and incident data.
- LLM Reasoning Service returns fallback answers if the model provider is unavailable.
- Chat API may show warnings such as:

```text
LLM service unavailable; deterministic fallback used: ReadTimeout from http://llm-reasoning:8002/generate
```

This mode is acceptable for demonstrating service orchestration, retrieval, guardrails, logs, and fallback behavior. It is not a full LLM-generation demo.

### 4.6 Alternative Option: Use a Remote Model Endpoint

If the model is running on another machine, update `.env`:

```text
LLM_BASE_URL=http://<remote-host>:8080/v1
LLM_MODEL=LiquidAI/LFM2.5-1.2B-Instruct
LLM_API_KEY=
```

Then restart Docker Compose:

```powershell
docker compose down
docker compose up --build
```

The remote endpoint must expose an OpenAI-compatible chat completions API.

## 5. Service URLs

| Service | URL | Swagger |
| --- | --- | --- |
| Frontend / Chat API | `http://localhost:8000/` | `http://localhost:8000/docs` |
| RAG Retrieval | `http://localhost:8001` | `http://localhost:8001/docs` |
| LLM Reasoning | `http://localhost:8002` | `http://localhost:8002/docs` |
| Mock Data | `http://localhost:8003` | `http://localhost:8003/docs` |

## 6. Smoke Tests

### Browser Test

Open:

```text
http://localhost:8000/
```

Login with:

```text
hana / 123
```

Try:

```text
CVD-05 triggered GAS012 during deposition. Should I escalate?
```

### API Test

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Etcher-03 triggered RF101 during plasma ignition. What should I check first?","configuration":"all"}'
```

On Windows PowerShell:

```powershell
curl.exe -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"Etcher-03 triggered RF101 during plasma ignition. What should I check first?\",\"configuration\":\"all\"}"
```

### Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## 7. Logs

Docker Compose writes JSON-line logs into:

| Service | Log File |
| --- | --- |
| Chat API | `logs/chat-api.log` |
| RAG Retrieval | `logs/rag-retrieval.log` |
| LLM Reasoning | `logs/llm-reasoning.log` |
| Mock Data | `logs/mock-data.log` |

Useful log checks:

```bash
tail -n 50 logs/chat-api.log
tail -n 50 logs/llm-reasoning.log
```

LLM Reasoning logs include:

- `llm_provider_request`
- `llm_provider_response`
- `llm_provider_error`

API keys are not logged.

## 8. Common Issues

### `python: command not found`

Use:

```bash
python3 --version
```

Then run MLX commands with `python3`.

### `No module named mlx_lm`

Install MLX in the active virtual environment:

```bash
pip install mlx-lm
```

### Cannot connect to `localhost:8080`

The macOS MLX model server is not running. Start it:

```bash
python3 -m mlx_lm.server \
  --model LiquidAI/LFM2.5-1.2B-Instruct \
  --host 0.0.0.0 \
  --port 8080
```

### Cannot connect to `localhost:11434`

The Windows Ollama service is not running. Start Ollama from the Windows app or run:

```powershell
ollama serve
```

Verify:

```powershell
curl.exe http://localhost:11434/v1/models
```

### Ollama says model not found

Check local model names:

```powershell
ollama list
```

Set `.env` `LLM_MODEL` to one of the names shown by `ollama list`.

### Docker service shows LLM fallback warning

Check whether the model endpoint is reachable.

For macOS MLX:

```bash
curl http://localhost:8080/v1/models
```

For Windows Ollama:

```powershell
curl.exe http://localhost:11434/v1/models
```

Then check:

```bash
tail -n 50 logs/llm-reasoning.log
tail -n 50 logs/chat-api.log
```

If the model is slow, make sure:

```text
LLM_TIMEOUT_SECONDS=30
SERVICE_TIMEOUT_SECONDS=45
```

### Port already in use

Stop old containers:

```bash
docker compose down
```

Then restart:

```bash
docker compose up --build
```

## 9. Run Tests

If Python dependencies are available locally:

```bash
pytest
```

The expected current result is:

```text
11 passed
```

## 10. Deployment Summary

Recommended reviewer flow:

1. Start or configure an OpenAI-compatible model endpoint.
2. Copy `.env.example` to `.env`.
3. Run `docker compose up --build`.
4. Open `http://localhost:8000/`.
5. Login with `hana / 123`.
6. Use sample questions from `document/SAMPLE_QUESTIONS_AND_ANSWERS.md`.

If no model endpoint is available, the app still demonstrates retrieval, structured data lookup, ID guardrails, deterministic fallback, logs, and Swagger APIs.

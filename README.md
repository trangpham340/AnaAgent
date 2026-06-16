# Analysis Agent AI

FastAPI project for a project-analysis AI agent. The API accepts project text,
requirements, notes, or source summaries and returns risks, recommendations, next
steps, and a concise summary.

## Setup

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
```

Add your real API key to `.env`. Use `.env.template` or `.env.example` as the dummy
template:

```env
OPENAI_API_KEY=your-real-key
```

## Run

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Streamlit UI

Start the FastAPI backend first:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In another terminal, run the UI:

```powershell
$env:API_BASE_URL="http://localhost:8000"
streamlit run streamlit_app.py
```

Open `http://localhost:8501`. The UI calls the FastAPI `/api/v1/analyze`
endpoint and uses the same backend business logic as the API.

## Docker

```powershell
docker compose up --build
```

`docker-compose.yml` loads runtime configuration from `.env`.
The container listens on port `8080`, which matches the AgentBase Runtime contract.
The Streamlit UI is available at `http://localhost:8501` when using Docker
Compose.

For plain Docker:

```powershell
docker build -t anaagent:latest .
docker run --env-file .env -p 8000:8080 anaagent:latest
```

## Test

```powershell
pytest
```

## Example Request

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/v1/analyze `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"project_name":"Demo","content":"Build a customer support chatbot.","goals":["Reduce response time"],"constraints":["Small team"]}'
```

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

## Docker

```powershell
docker compose up --build
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

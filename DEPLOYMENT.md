# Deployment Guide — AI Document Classifier

## Prerequisites
- Docker Desktop
- Azure CLI (`az --version`)
- Azure subscription
- Groq API key

## Azure Resources

| Resource | Name | Resource Group |
|---|---|---|
| Container Registry | `aiclassifierregistry` | `ai-classifier-rg` |
| Container App | `ai-classifier-app` | `ai-classifier-rg` |
| Container Apps Env | `studyrag-env` | `studyrag-rg` (shared) |
| PostgreSQL | Neon (ai_classifier db) | neon.tech |

## Step 1 — Train ML Model

```bash
python -m backend.training.train_model
```

Required before building Docker image.

## Step 2 — Build & Push Image

```bash
az acr login --name aiclassifierregistry
docker build -t aiclassifierregistry.azurecr.io/ai-classifier:latest .
docker push aiclassifierregistry.azurecr.io/ai-classifier:latest
```

## Step 3 — Deploy New Revision

```bash
az containerapp update \
  --name ai-classifier-app \
  --resource-group ai-classifier-rg \
  --image aiclassifierregistry.azurecr.io/ai-classifier:latest
```

## Environment Variables (Azure)

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `JWT_SECRET_KEY` | 64-char hex secret |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `GROQ_MODEL` | `llama-3.1-8b-instant` |
| `UPLOAD_DIR` | `/tmp/uploads` |
| `LOG_DIR` | `/tmp/logs` |
| `MODEL_DIR` | `/app/backend/training/models` |
| `LLM_CONFIDENCE_THRESHOLD` | `0.75` |
| `MAX_FILE_SIZE_MB` | `10` |

## Make User Admin (Azure Console)

```bash
python -c "
import sys
sys.path.insert(0, '/app/backend')
from db.database import SessionLocal
from db.models import User
db = SessionLocal()
user = db.query(User).filter(User.email == 'your@email.com').first()
user.is_admin = True
db.commit()
print('Done:', user.email)
db.close()
"
```

## Cold Start Note

Min replicas = 0 (scale to zero). First request after idle takes ~30 seconds.

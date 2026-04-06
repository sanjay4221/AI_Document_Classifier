# Changelog — AI Document Classifier

## [1.0.0] — April 2026

### Phase 1 — Project Scaffold
- Full enterprise folder structure
- Docker, docker-compose, gitignore setup

### Phase 2 — Core Layer
- Config, logger (rotating file + audit), security, exceptions, rate limiter

### Phase 3 — Database + API
- Neon PostgreSQL + SQLite local auto-switch
- Users, Documents, ClassificationResults schema
- Auth routes (register, login, me)
- Document routes (upload, list, delete, reclassify)
- Classification routes (classify, result)
- Admin routes (stats, users, classifications)

### Phase 4 — Classifier Layer
- PDF extraction (pdfplumber + PyPDF2 fallback)
- Text preprocessing (clean, normalise, truncate)
- Groq LLM classifier (few-shot prompting)
- scikit-learn ML classifier (TF-IDF + Logistic Regression)
- Hybrid decision engine (ML-first, cost optimised)
- Pinecone store (stubbed for future)
- 72 synthetic training examples (12 per department)

### Phase 5 — Main App
- FastAPI app wiring, CORS, static files, startup events

### Phase 6 — Frontend
- Modern purple/gradient dark theme
- Drag & drop upload with bulk progress
- Card-based layout with result panel
- All 6 department confidence bar chart
- Confidence warnings (high/medium/low)
- Department filter pills
- Dark/light mode toggle
- CSV + PDF export
- Delete document (bin icon)
- Reclassify button

### Phase 7 — Docker + Azure
- Dockerfile with baked ML models
- Azure Container Registry
- Azure Container Apps deployment
- Environment variable configuration

## Planned
- Pinecone similarity search
- Batch processing
- OAuth login
- Mobile responsive UI
- Retrain on real data pipeline

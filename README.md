<div align="center">

# 🧠 AI Document Classifier

### Enterprise-grade AI-powered document classification system

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036?style=flat&logo=groq&logoColor=white)](https://groq.com)
[![Azure](https://img.shields.io/badge/Azure-Container_Apps-0078D4?style=flat&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com)
[![PostgreSQL](https://img.shields.io/badge/Neon-PostgreSQL-00E699?style=flat&logo=postgresql&logoColor=white)](https://neon.tech)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat)](LICENSE)

**[🌐 Live Demo](https://ai-classifier-app.prouddune-47b5fd2b.australiaeast.azurecontainerapps.io) · [📖 API Docs](https://ai-classifier-app.prouddune-47b5fd2b.australiaeast.azurecontainerapps.io/docs) · [🐛 Report Bug](https://github.com/sanjay4221/AI_Document_Classifier/issues)**

![AI Document Classifier Demo](Documents/demo-screenshot.png)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)

---

## 🎯 Overview

AI Document Classifier is a production-ready web application that automatically classifies business PDF documents into departments using a **Hybrid AI approach** — combining Groq LLaMA LLM with a trained scikit-learn ML model.

### The Problem It Solves

Organisations accumulate thousands of unclassified documents — invoices, contracts, HR letters, compliance reports — sitting in shared drives with no structure. Manual classification is slow, inconsistent, and expensive.

This system automates that process with **enterprise-level accuracy and explainability**.

### Classification Departments

| Department | Example Documents |
|---|---|
| 💰 Finance | Invoices, budgets, audit reports, tax documents |
| 👥 Human Resources | Employment contracts, payslips, performance reviews |
| ⚖️ Legal & Regulatory | NDAs, contracts, court orders, regulatory submissions |
| 📋 Licensing & Compliance | Licenses, permits, certifications, compliance checklists |
| 💻 IT & Technology | System specs, security policies, incident reports |
| ⚙️ Operations | SOPs, maintenance logs, vendor agreements |

---

## ✨ Features

- 🤖 **Hybrid AI Classification** — Groq LLaMA LLM + scikit-learn ML fallback
- 💰 **Cost Optimised** — ML-first approach reduces LLM API calls by ~70%
- 📊 **Confidence Scoring** — Visual confidence meter with warning banners
- 🔄 **Reclassify** — Re-run classification on any document
- 📥 **Export Results** — Download as CSV or PDF report
- 🔍 **Department Filter** — Filter documents by department
- 🌙 **Dark/Light Mode** — Persisted theme preference
- 👤 **JWT Authentication** — Secure login with role-based access
- 🛡️ **Admin Dashboard** — User management, stats, audit logs
- 📈 **Audit Trail** — Every classification logged with method and confidence
- 🐳 **Docker Ready** — Single command deployment
- ☁️ **Azure Deployed** — Live on Azure Container Apps

---

## 🏗️ Architecture

```
refer : ai-classifier\documents\AIML_Classifier_Architect_Flow.pdf
```

### Hybrid Classification Logic

```
refer : ai-classifier\documents\Classsify_Hybrid_Flow_AIML.pdf
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **LLM** | Groq API — LLaMA 3.1-8b-instant |
| **ML Model** | scikit-learn — TF-IDF + Logistic Regression |
| **PDF Extraction** | pdfplumber + PyPDF2 |
| **Database** | Neon PostgreSQL (cloud) / SQLite (local) |
| **Auth** | JWT (python-jose) + bcrypt |
| **Rate Limiting** | slowapi |
| **Frontend** | Vanilla JS, HTML5, CSS3 |
| **Container** | Docker |
| **Cloud** | Azure Container Apps |
| **Vector DB** | Pinecone (future similarity search) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Groq API Key](https://console.groq.com) (free)
- Git

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/sanjay4221/AI_Document_Classifier.git
cd AI_Document_Classifier

# 2. Create virtual environment
python -m venv .venv --without-pip
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 3. Install pip and dependencies
python -m ensurepip --upgrade
pip install -r backend/requirements.txt

# 4. Configure environment
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
# Edit .env and add your GROQ_API_KEY and JWT_SECRET_KEY

# 5. Train the ML model (run once)
python -m backend.training.train_model

# 6. Start the server
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000/login.html`

### Generate JWT Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📁 Project Structure

```
refer : ai-classifier\documents\Project_Structure.pdf
```

---

## 📊 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Get JWT token |
| GET | `/auth/me` | JWT | Current user |
| POST | `/documents/upload` | JWT | Upload PDF |
| GET | `/documents/` | JWT | List documents |
| DELETE | `/documents/{id}` | JWT | Delete document |
| POST | `/documents/{id}/reclassify` | JWT | Reclassify document |
| POST | `/classify/{id}` | JWT | Run classification |
| GET | `/classify/{id}/result` | JWT | Get result |
| GET | `/health` | No | Health check |
| GET | `/admin/stats` | Admin | System statistics |
| GET | `/admin/users` | Admin | All users |

Full interactive docs: **[/docs](https://ai-classifier-app.prouddune-47b5fd2b.australiaeast.azurecontainerapps.io/docs)**

---

## 🐳 Deployment

### Docker (Local)

```bash
docker build -t ai-classifier .
docker run -p 8000:8000 --env-file .env ai-classifier
```

### Azure Container Apps

```bash
# Login
az login
az acr login --name aiclassifierregistry

# Build and push
docker build -t aiclassifierregistry.azurecr.io/ai-classifier:latest .
docker push aiclassifierregistry.azurecr.io/ai-classifier:latest

# Deploy new revision
az containerapp update \
  --name ai-classifier-app \
  --resource-group ai-classifier-rg \
  --image aiclassifierregistry.azurecr.io/ai-classifier:latest
```

Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🗺️ Roadmap

- [x] Hybrid LLM + ML classification
- [x] Confidence scoring with warnings
- [x] JWT authentication
- [x] Admin dashboard
- [x] Docker + Azure deployment
- [x] Dark/light mode
- [x] Department filtering
- [x] CSV/PDF export
- [x] Delete + reclassify
- [x] Reset paswword using render.com
- [ ] Pinecone similarity search
- [ ] Batch processing (50+ docs)
- [ ] OAuth (Google login)
- [ ] Webhook notifications
- [ ] Mobile responsive UI
- [ ] Retrain on real classified data

---

## 👤 Author

**Sanjay Kumar**
- GitHub: [@sanjay4221](https://github.com/sanjay4221)
- Email: sanjayetc.kumar008@gmail.com

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built using FastAPI, Groq, and Azure
</div>

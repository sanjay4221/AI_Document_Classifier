"""
template.py — Project Scaffolding Script
AI Document Classifier
Run once to create the full folder + file structure.
Usage: python template.py
"""

import os

# ── Folder structure ──────────────────────────────────────────
FOLDERS = [
    "backend/api/routes",
    "backend/core",
    "backend/db",
    "backend/classifier",
    "backend/training/models",
    "backend/tests",
    "frontend/css",
    "frontend/js",
    "logs",
    "uploads",
]

# ── Files to create (empty if not exists) ─────────────────────
FILES = [
    # Root
    ".env.example",
    ".gitignore",
    ".dockerignore",
    "Dockerfile",
    "docker-compose.yml",
    "README.md",
    "DEPLOYMENT.md",
    "CHANGELOG.md",

    # Backend root
    "backend/main.py",
    "backend/requirements.txt",
    "backend/pytest.ini",

    # API layer
    "backend/api/__init__.py",
    "backend/api/deps.py",
    "backend/api/routes/__init__.py",
    "backend/api/routes/auth.py",
    "backend/api/routes/documents.py",
    "backend/api/routes/classify.py",
    "backend/api/routes/health.py",
    "backend/api/routes/admin.py",

    # Core layer
    "backend/core/__init__.py",
    "backend/core/config.py",
    "backend/core/exceptions.py",
    "backend/core/limiter.py",
    "backend/core/logger.py",
    "backend/core/security.py",

    # DB layer
    "backend/db/__init__.py",
    "backend/db/models.py",
    "backend/db/database.py",
    "backend/db/crud.py",

    # Classifier layer
    "backend/classifier/__init__.py",
    "backend/classifier/extractor.py",
    "backend/classifier/preprocessor.py",
    "backend/classifier/groq_classifier.py",
    "backend/classifier/ml_classifier.py",
    "backend/classifier/hybrid.py",
    "backend/classifier/pinecone_store.py",

    # Training
    "backend/training/__init__.py",
    "backend/training/synthetic_data.py",
    "backend/training/train_model.py",
    "backend/training/models/.gitkeep",

    # Tests
    "backend/tests/__init__.py",
    "backend/tests/conftest.py",
    "backend/tests/test_auth.py",
    "backend/tests/test_documents.py",
    "backend/tests/test_classifier.py",
    "backend/tests/test_hybrid.py",

    # Frontend
    "frontend/index.html",
    "frontend/login.html",
    "frontend/admin.html",
    "frontend/privacy.html",
    "frontend/terms.html",
    "frontend/css/style.css",
    "frontend/js/app.js",
    "frontend/js/auth.js",
    "frontend/js/admin.js",

    # Gitkeeps
    "logs/.gitkeep",
    "uploads/.gitkeep",
]


def create_structure():
    print("\n🚀 AI Document Classifier — Project Scaffold")
    print("=" * 50)

    # Create folders
    print("\n📁 Creating folders...")
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
        print(f"   ✅ {folder}/")

    # Create files
    print("\n📄 Creating files...")
    created = 0
    skipped = 0
    for file_path in FILES:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                pass  # empty file
            print(f"   ✅ {file_path}")
            created += 1
        else:
            print(f"   ⏭️  {file_path} (already exists, skipped)")
            skipped += 1

    print("\n" + "=" * 50)
    print(f"✅ Done! {created} files created, {skipped} skipped.")
    print("\n📌 Next steps:")
    print("   1. cd D:\\Py_Projects\\ai-classifier")
    print("   2. python -m venv .venv")
    print("   3. .venv\\Scripts\\activate")
    print("   4. pip install -r backend/requirements.txt")
    print("   5. Copy .env.example → .env and fill in your keys")
    print("   6. uvicorn backend.main:app --reload --port 8000")
    print()


if __name__ == "__main__":
    create_structure()
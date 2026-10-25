# StudyPal Developer Guide

## 1. Local Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (tested on v20.19.6)
- `uv` package manager

### Installation Commands
```bash
# Set up Python virtual environment
uv venv .venv --python 3.11
.venv\Scripts\activate       # On Windows
# source .venv/bin/activate  # On Linux/macOS

# Install backend dependencies
uv pip install -e ".[dev]" email-validator

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## 2. Seeding & Running Tests

```bash
# Seed demo student account and realistic curriculum notes
python scripts/seed_demo_data.py

# Run all unit and API integration tests
pytest backend/tests/unit backend/tests/api

# Run ML experimentation benchmark
python scripts/run_evaluation.py
```

## 3. Running Dev Servers

- **Backend API**:
  ```bash
  python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
  ```
- **Frontend App**:
  ```bash
  cd frontend
  npm run dev
  ```
  Access at `http://127.0.0.1:5173`.

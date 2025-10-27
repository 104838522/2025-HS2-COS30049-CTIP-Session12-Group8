# Vulnerability Locator – Full Stack

This branch combines the FastAPI backend and the React frontend in a single workspace so you can run the app end-to-end without juggling multiple checkouts.

## Repository layout

- `main.py`, `preprocess.py`, `model_loader.py`, `model_knn_save.py`, `models.zip`, `vectorizer.pkl` – backend sources and assets.
- `frontend/` – React application that ships the VulnLocator UI.
- `scripts/dev.sh` – helper script that launches both servers locally.

## Initial setup

1. **Backend Python deps**
   ```bash
   cd /path/to/repo
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install fastapi uvicorn[standard] joblib numpy scipy pandas scikit-learn python-multipart
   unzip -o models.zip
   ```

2. **Frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

## Run everything together

From the repository root (with your virtual env active):
```bash
scripts/dev.sh
```

The script starts:
- FastAPI at `http://127.0.0.1:8000` (reload enabled).
- React dev server at `http://localhost:3000`.

Press `Ctrl+C` once to stop both processes. You can override defaults via environment variables, e.g.:
```bash
BACKEND_PORT=9000 UVICORN_APP=main:app scripts/dev.sh
```

## Manual commands (optional)

If you prefer to run services separately:
```bash
# Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend
npm start
```

Visit `http://localhost:3000` and the UI will proxy requests to the backend CORS origin at `http://127.0.0.1:8000`.

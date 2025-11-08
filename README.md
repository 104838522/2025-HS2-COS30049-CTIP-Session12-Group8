# Vulnerability Locator – AI-Powered Software Vulnerability Detector
Team:2025-HS2-COS30049-CTIP-Session12-Group8
GitHub link: https://github.com/104838522/2025-HS2-COS30049-CTIP-Session12-Group8/tree/full-stack

Description:
This project is a full-stack web application built with React.js (front-end) and FastAPI (back-end).
It integrates an AI model (KNN and Random Forest) to detect software vulnerabilities in source code.
Users can submit code through the interface, receive predictions in real-time, and visualize AI results with interactive D3.js charts.

Key Features:
- Real-time AI-based vulnerability detection for source code
- Three visualization charts showing confidence, vulnerability scores, and historical trends
- Authentication system (Sign up, Login, Token verification)
- RESTful FastAPI back-end with error handling and middleware for request logging
- Interactive D3 visualizations for explainable AI results
- Memory-based user data management with token-based access control

## Repository layout

vulnlocator/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │        ├── endpoints/
│   │   │        │   ├── analyze.py          # Handles AI predictions for uploaded or typed code
│   │   │        │   ├── auth.py             # User signup, login, and token generation
│   │   │        │   ├── history.py          # Retrieves and deletes user analysis history
│   │   │        │   ├── user.py             # User profile management (update name/password)
│   │   │        │   └── visualization.py    # Provides data for visualization charts
│   │   │        │
│   │   │        └── __init__.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                     # Middleware & request timing logs
│   │   │   ├── exceptions.py                 # Global error handling (JSON response)
│   │   │   └── helpers.py                    # Token generation & verification
│   │   │
│   │   ├── db/
│   │   │   └── memory_db.py                  # In-memory storage for users & history
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py                    # Pydantic data validation schemas
│   │   │
│   │   ├── services/
│   │   │   └── ai_service.py                 # Loads & executes AI models
│   │   │
│   │   ├── utils/
│   │   │   └── preprocess.py                 # Preprocessing function for input code
│   │   │
│   │   ├── main.py                           # FastAPI entry point
│   │   └── __init__.py
│   │       
│   │─── ml_models/                        # Stored AI models and scalers
│   │  ├── model_knn_save.py                     # Script to save KNN model
│   │  ├── model_rf_save.py                      # Script to save RF model
│   │  ├── vectorizer.pkl                        # Pre-trained token vectorizer
│   │  ├── knn_model.joblib
│   │  ├── rf_model.joblib
│   │  ├── knn_scaler.joblib
│   │  └── rf_scaler.joblib
│   │
│   └─── data/
│       └── processed_dataset_final.csv.gz  # Data for model_knn_save.py & model_rf_save.py and visualization endpoint
│    
│
├── frontend/
│   ├── node_modules/
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── ...
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/                       # D3-based visualization components
│   │   │   │   ├── ConfidencePieChart.js     # Displays prediction confidence ratio
│   │   │   │   ├── HistoryConfidenceChart.js # Time-based confidence trend
│   │   │   │   ├── LangDistributionChart.js  # Language distribution stats
│   │   │   │   ├── ScoreBarChart.js          # Vulnerability score by line number
│   │   │   │   └── TokenFrequencyChart.js    # Token-level safe/vulnerable counts
│   │   │   ├── LoginOverlay.js               # Modal login overlay component
│   │   │   └── SettingsDialog.js             # User settings dialog box
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.js                # Handles global auth state and token Signup and Login
│   │   │
│   │   ├── pages/                            # Main route-level pages
│   │   │   ├── DatasetInfoPage.js            # Dataset summary and info
│   │   │   ├── HistoryPage.js                # User analysis history + chart
│   │   │   ├── KnowledgePage.js              # AI knowledge base view
│   │   │   ├── LayoutPage.js                 # Main layout wrapper with navbar
│   │   │   └── ProfilePage.js                # User profile and update page
│   │   │
│   │   ├── utils/
│   │   │   └── theme.js                      # Custom MUI theme configuration
│   │   │
│   │   ├── App.css                           # Global style
│   │   ├── App.js                            # Main app structure and router
│   │   ├── App.test.js
│   │   ├── index.css
│   │   ├── index.js                          # React entry point
│   │   ├── reportWebVitals.js
│   │   └── setupTests.js
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── README.md
│
├── scripts/
├── test-samples/
├── .gitignore
└── README.md

## Initial setup

1. **Backend Python deps**
   for Windows
   ```bash
   cd /path/to/repo/backend/ml_models
   python model_knn_save.py
   python model_rf_save.py
   cd /path/to/repo/backend
   python -m venv .venv
   .venv\Scripts\Activate
   pip install --upgrade pip
   pip install fastapi uvicorn pandas numpy scikit-learn joblib imbalanced-learn python-multipart
   ```
   
   for macOS/Linux
   ```bash
   cd /path/to/repo/backend/ml_models
   python model_knn_save.py
   python model_knn_save.py
   cd /path/to/repo/backend
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install fastapi uvicorn pandas numpy scikit-learn joblib imbalanced-learn python-multipart
   ```

2. **Frontend dependencies**
   ```bash
   cd /path/to/repo/frontend
   npm install
   ```

3. **Run the ML models**
## Run everything together (for macOS/Linux)

From the repository root (with your virtual env active):
```bash
./scripts/dev.sh
```

The script starts:
- FastAPI at `http://127.0.0.1:8000` (reload enabled).
- React dev server at `http://localhost:3000`.

Press `Ctrl+C` once to stop both processes. You can override defaults via environment variables, e.g.:
```bash
BACKEND_PORT=9000 UVICORN_APP=main:app scripts/dev.sh
```

## Manual commands (optional or for Windows)

If you prefer to run services separately:
```bash
# Backend
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm start
```

Visit `http://localhost:3000` and the UI will proxy requests to the backend CORS origin at `http://127.0.0.1:8000`.

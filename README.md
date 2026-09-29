# Plataforma de videos (React + FastAPI + AWS)

## Backend (local)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Documentación: http://127.0.0.1:8000/docs

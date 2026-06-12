# =========================
# BACKEND DOCKER IMAGE
# =========================

FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend
CMD ["python", "app.py"]
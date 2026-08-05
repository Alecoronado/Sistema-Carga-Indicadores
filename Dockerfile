# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy Excel data for initial seeding
COPY FONPLATA_Modelo_Datos_2026_1.xlsx ./

EXPOSE 8000

CMD ["sh", "-c", "cd backend && python import_excel.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

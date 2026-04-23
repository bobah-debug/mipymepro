FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc libxml2-dev libxslt-dev libffi-dev \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-builder /frontend/dist /app/frontend_dist

ENV FRONTEND_BUILD_DIR=/app/frontend_dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

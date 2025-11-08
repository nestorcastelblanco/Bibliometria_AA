#!/bin/bash
# Script para desplegar en Google Cloud Run

set -e

# Variables
PROJECT_ID="tu-proyecto-gcp"
SERVICE_NAME="bibliometria-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Iniciando despliegue en Google Cloud Run..."
echo "================================================"

# 1. Build de la imagen
echo "📦 Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME} --project=${PROJECT_ID}

# 2. Deploy a Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=bibliometria_web.settings_production" \
    --set-env-vars "SECRET_KEY=$(openssl rand -base64 32)" \
    --project=${PROJECT_ID}

echo "✅ Despliegue completado!"
echo "================================================"
echo "URL del servicio:"
gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format "value(status.url)" \
    --project=${PROJECT_ID}

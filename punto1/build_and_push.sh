#!/bin/bash
set -e # Esto hace que el script falle si un comando falla

# --- ¡CONFIGURA ESTAS 3 VARIABLES! ---
AWS_ACCOUNT_ID="989496898827"  # <-- REEMPLAZA con tu ID de cuenta de 12 dígitos
AWS_REGION="us-east-1"      # <-- REEMPLAZA con tu región (ej: us-east-1)
IMAGE_NAME="lambda-fastapi-final" # <-- Nombre para tu imagen/repositorio
# ------------------------------------------

# Construir la URL completa del repositorio en ECR (Elastic Container Registry)
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
IMAGE_URI="$ECR_URI/$IMAGE_NAME:latest"

echo "URI de la imagen: $IMAGE_URI"

# 1. Autenticar Docker con el registro ECR de AWS
echo "Autenticando Docker con ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# 2. Crear el repositorio en ECR (si no existe, no da error)
echo "Creando repositorio ECR (si es necesario)..."
aws ecr create-repository \
    --repository-name $IMAGE_NAME \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --image-tag-mutability MUTABLE > /dev/null 2>&1 || true

# 3. (Paso b.i y b.ii) Construir la imagen de Docker y etiquetarla como 'latest'
echo "Construyendo imagen Docker..."
docker build -t $IMAGE_URI .

# 4. (Paso b.iii) Subir la imagen al container registry (ECR)
echo "Subiendo imagen a ECR..."
docker push $IMAGE_URI

echo "---"
echo "¡Éxito! Imagen subida correctamente a ECR."
echo "Repositorio: $IMAGE_NAME"
echo "URI Completa: $IMAGE_URI"
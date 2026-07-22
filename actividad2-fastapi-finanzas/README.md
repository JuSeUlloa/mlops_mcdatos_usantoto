# FASTAPI FINANZAS

API REST para análisis financiero y predicción de precios de acciones usando datos de Yahoo Finance.

## Características

- Gráficos históricos de precios (1 año, período personalizado)
- Predicción de precios a 7 días
- Múltiples tipos de visualización (línea, área, barras)
- Normalización automática de períodos
- Despliegue continuo en GCP Cloud Run

## Estructura del Proyecto

```
actividad2-fastapi-finanzas/
├── src/
│   ├── main.py                    # Aplicación FastAPI principal
│   ├── routes/
│   │   ├── charts.py              # Endpoints de gráficos
│   │   └── forecast.py            # Endpoints de predicción
│   └── services/
│       ├── yahoo_services.py      # Servicio de datos Yahoo Finance
│       └── obtain_forecast.py     # Servicio de predicción
├── pyproject.toml                 # Dependencias del proyecto
├── Dockerfile                     # Configuración Docker
└── .github/workflows/
    └── deploy.yml                 # Pipeline CI/CD
```

## Endpoints

### Gráficos Históricos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/charts/history/{ticker}` | Gráfico de 1 año (línea) |
| GET | `/charts/history/{ticker}/{period}` | Gráfico por período |

**Períodos soportados:**
- Días: `5d`, `10d`, `15d`, etc.
- Meses: `1mo`, `3mo`, `6mo`, etc.
- Años: `1y`, `2y`, `5y`, etc.

**Normalización automática:**
- `30d` → `1mo` (gráfico de línea con marcadores)
- `60d` → `2mo` (gráfico de línea con marcadores)
- `25mo` → `2y` (gráfico de área)
- `36mo` → `3y` (gráfico de área)

**Tipos de gráficos:**
- **Días (< 30)**: Línea roja
- **Meses (30d - 12mo)**: Línea verde con marcadores y relleno
- **Años (≥ 12mo)**: Área azul con relleno

### Predicción

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/forecast/forecast/{ticker}` | Predicción a 7 días |

**Ejemplo de respuesta:**
```json
{
  "ticker": "AAPL",
  "forecast": [
    {"day": 1, "close_forecast": 185.23},
    {"day": 2, "close_forecast": 186.45},
    ...
  ]
}
```

### Salud

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de estado |
| GET | `/health` | Verificación de salud |

## Instalación Local

### Requisitos

- Python 3.11+
- uv (gestor de paquetes)

### Pasos

```bash
# Clonar repositorio
git clone <repo-url>
cd actividad2-fastapi-finanzas

# Instalar dependencias
uv sync

# Ejecutar servidor de desarrollo
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

**Documentación interactiva:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## CI/CD - Despliegue Continuo

### Arquitectura

```
GitHub → GitHub Actions → Artifact Registry → Cloud Run
  ↓           ↓                  ↓                ↓
 Push     Build & Test    Docker Image      API Pública
```

### Flujo de Despliegue

1. **Trigger**: Push a rama `main` en archivos de `actividad2-fastapi-finanzas/`
2. **Build**: Construcción de imagen Docker con dependencias
3. **Push**: Subida de imagen a Google Artifact Registry
4. **Deploy**: Despliegue en Google Cloud Run
5. **Verify**: Verificación automática con health check

### Configuración en GCP

**1. Crear proyecto y habilitar APIs:**
```bash
gcloud projects create smartportfolio-api
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

**2. Crear Artifact Registry:**
```bash
gcloud artifacts repositories create mlops_mcdatos_usantoto \
  --repository-format=docker \
  --location=us-central1
```

**3. Configurar Workload Identity Federation:**
```bash
# Crear service account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions SA"

# Habilitar APIs necesarias
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com

# Crear pool de workload identity
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Crear provider para GitHub
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='tu-usuario/tu-repo'"

# Asignar permisos
gcloud iam service-accounts add-iam-policy-binding github-actions-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/tu-usuario/tu-repo"

# Asignar roles necesarios
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### Permisos de la Service Account

La service account utilizada por GitHub Actions requiere los siguientes permisos:

#### APIs Habilitadas

| API | ID | Propósito |
|-----|-----|-----------|
| Cloud Run Admin API | `run.googleapis.com` | Desplegar y gestionar servicios Cloud Run |
| Artifact Registry API | `artifactregistry.googleapis.com` | Almacenar imágenes Docker |
| IAM Credentials API | `iamcredentials.googleapis.com` | Generar credenciales para Workload Identity |
| Security Token Service API | `sts.googleapis.com` | Intercambiar tokens OIDC |
| Cloud Build API | `cloudbuild.googleapis.com` | (Opcional) Para builds en GCP |

**Comando para habilitar todas las APIs:**
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  --project=PROJECT_ID
```

#### Roles IAM Requeridos

| Rol | ID | Propósito |
|-----|-----|-----------|
| Cloud Run Admin | `roles/run.admin` | Crear, actualizar y desplegar servicios en Cloud Run |
| Artifact Registry Writer | `roles/artifactregistry.writer` | Subir imágenes Docker a Artifact Registry |
| IAM Service Account User | `roles/iam.serviceAccountUser` | Usar la service account en despliegues |
| IAM Workload Identity User | `roles/iam.workloadIdentityUser` | Permitir autenticación desde GitHub Actions |

**Comando para asignar todos los roles:**
```bash
PROJECT_ID="tu-project-id"
SA_EMAIL="github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Roles para la service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"

# Permisos de Workload Identity
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/tu-usuario/tu-repo"
```

#### Verificación de Permisos

**Verificar APIs habilitadas:**
```bash
gcloud services list --enabled --project=PROJECT_ID
```

**Verificar roles asignados a la service account:**
```bash
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

**Verificar configuración de Workload Identity:**
```bash
# Ver pool
gcloud iam workload-identity-pools describe github-pool \
  --location="global"

# Ver provider
gcloud iam workload-identity-pools providers describe github-provider \
  --location="global" \
  --workload-identity-pool="github-pool"

# Ver permisos de la service account
gcloud iam service-accounts get-iam-policy github-actions-sa@PROJECT_ID.iam.gserviceaccount.com
```

#### Solución de Problemas Comunes

**Error: "API not enabled"**
```bash
# Habilitar la API específica
gcloud services enable run.googleapis.com --project=PROJECT_ID
```

**Error: "Permission denied"**
```bash
# Verificar que la service account tiene los roles correctos
gcloud projects get-iam-policy PROJECT_ID \
  --filter="bindings.members:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com"
```

**Error: "Workload Identity Federation failed"**
```bash
# Verificar que el attribute-condition coincide con tu repositorio
gcloud iam workload-identity-pools providers describe github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(attributeCondition)"
```
  --member="serviceAccount:github-actions-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

**4. Configurar secretos en GitHub:**

Ir a `Settings → Secrets and variables → Actions` y agregar:

| Secreto | Valor |
|---------|-------|
| `GCP_PROJECT_ID` | ID del proyecto en GCP |

### Workflow de GitHub Actions

El archivo `.github/workflows/deploy.yml` ejecuta automáticamente:

```yaml
name: Financial Deploy API

on:
  push:
    branches: [main]
    paths:
      - 'actividad2-fastapi-finanzas/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout del código
      - Autenticación con GCP (Workload Identity)
      - Build de imagen Docker
      - Push a Artifact Registry
      - Deploy a Cloud Run
      - Verificación con health check
```

### Despliegue Manual

Para ejecutar el workflow manualmente:

1. Ir a `Actions` en GitHub
2. Seleccionar "Financial Deploy API"
3. Click en "Run workflow"

### Verificar Despliegue

```bash
# Obtener URL del servicio
gcloud run services describe fastapi-finanzas \
  --region=us-central1 \
  --format="value(status.url)"

# Probar endpoint
curl https://fastapi-finanzas-xxxxx-uc.a.run.app/health
```

## Docker

### Construcción Local

```bash
docker build -t smartportfolio-api .
docker run -p 8080:8080 smartportfolio-api
```

### Imagen en Artifact Registry

```bash
# Autenticar Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Pull de la imagen
docker pull us-central1-docker.pkg.dev/PROJECT_ID/mlops_mcdatos_usantoto/fastapi-finanzas:latest
```

## Tecnologías

- **Framework**: FastAPI
- **Servidor**: Uvicorn
- **Datos**: yfinance, pandas
- **Visualización**: matplotlib
- **Contenedores**: Docker
- **CI/CD**: GitHub Actions
- **Cloud**: Google Cloud Platform (Cloud Run, Artifact Registry)
- **Autenticación**: Workload Identity Federation

## Notas

- La predicción usa un modelo simple basado en media y desviación estándar
- Los gráficos se generan dinámicamente con matplotlib
- El servidor usa backend "Agg" para evitar problemas con GUI
- Los períodos se normalizan automáticamente para mejor visualización

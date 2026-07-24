# Financial API

API REST para análisis financiero y predicción de precios de acciones con datos de Yahoo Finance.

## Características

- Gráficos históricos de precios (1 año, período personalizado)
- Predicción de precios a 7 días (estadística)
- **3 Modelos de Machine Learning (RandomForest)**:
  - Predicción de dirección (clasificación: up/down)
  - Predicción de retorno porcentual (regresión)
  - Predicción de volatilidad (regresión)
- Normalización automática de períodos
- Despliegue continuo en GCP Cloud Run
- Soporte offline con datos cacheados
- Tracking de experimentos con MLflow

## Estructura del Proyecto

```
actividad2-fastapi-finanzas/
├── data/
│   ├── raw/                    # Datos crudos de Yahoo Finance
│   └── processed/              # Datos procesados con features
├── src/
│   └── financial_api/
│       ├── api.py              # Aplicación FastAPI principal
│       ├── data.py             # Descarga y procesamiento de datos
│       ├── features.py         # Ingeniería de features
│       ├── train.py            # Entrenamiento del modelo
│       ├── predict.py          # Servicio de predicción ML
│       ├── entities/           # Modelos Pydantic (schemas)
│       │   └── prediction.py   # PredictionRequest
│       ├── routes/             # Endpoints de la API
│       │   ├── charts.py       # Gráficos históricos
│       │   ├── forecast.py     # Predicción estadística
│       │   ├── market_data.py  # Datos de mercado
│       │   └── predict.py      # Predicción ML
│       └── services/           # Lógica de negocio
│           ├── yahoo_services.py    # Descarga de datos Yahoo Finance
│           └── obtain_forecast.py   # Predicción estadística
├── artifacts/                  # Modelos entrenados
├── tests/                      # Tests unitarios
├── reports/                    # Métricas y gráficos
├── Dockerfile                  # Configuración Docker
├── pyproject.toml              # Dependencias
└── README.md                   # Documentación
```

## Endpoints


| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de estado |
| GET | `/health` | verifica que la API esté viva  |

### Datos de Mercado

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/market-data/{ticker}/{period}` | Descargar y procesar datos (con fallback offline) |

**Ejemplo:**
```bash
http://localhost:8000/market-data/AAPL/5y
```

### Predicción con Machine Learning

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/predict/direction` | Predicción de dirección (up/down) con probabilidad real |
| POST | `/predict/return` | Predicción de retorno porcentual |
| POST | `/predict/volatility` | Predicción de volatilidad |
| GET | `/predict/model/{ticker}/{model_type}` | Información del modelo |

**Request body Aplica para las 3 peticiones Post:**
```json
{
  "symbol": "AAPL",
  "prediction_horizon": 1,
  "use_cached_data": true
}
```

**Ejemplo de respuesta - Dirección:**
```json
{
  "symbol": "AAPL",
  "prediction": "up",
  "probability_up": 0.63,
  "model_version": "randomforestclassifier_v1",
  "prediction_horizon": "next_day",
  "current_close": 185.23
}
```

**Ejemplo de respuesta - Retorno:**
```json
{
  "symbol": "AAPL",
  "predicted_return": 0.015,
  "predicted_return_pct": 1.5,
  "predicted_close": 188.01,
  "current_close": 185.23,
  "model_version": "randomforestregressor_v1",
  "prediction_horizon": "next_day"
}
```

**Ejemplo de respuesta - Volatilidad:**
```json
{
  "symbol": "AAPL",
  "predicted_volatility": 0.0234,
  "predicted_volatility_pct": 2.34,
  "model_version": "randomforestregressor_v1",
  "prediction_horizon": "next_day"
}
```

### Gráficos Históricos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/charts/history/{ticker}` | Gráfico de 1 año (línea) |

**Ejemplo:**
```bash
http://localhost:8000/charts/history/AAPL 
```

### Predicción Estadística

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/forecast/forecast/{ticker}` | Predicción estadística a 7 días |

**Ejemplo:**
```bash
http://localhost:8000/forecast/forecast/AAPL
```

## Instalación Local

### Requisitos

- Python 3.11+
- uv (gestor de paquetes)

### Pasos

```bash
# Clonar repositorio
git clone https://github.com/JuSeUlloa/mlops_mcdatos_usantoto.git
# Acceder al directorio del proyecto
cd actividad2-fastapi-finanzas
```
#### Activar entorno virtual

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```
### Librerias ejecución
```bash

# Instalar dependencias
uv sync

# Ejecutar servidor de desarrollo
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

**Documentación interactiva:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Comandos Rápidos

```bash
# 1. Instalar dependencias (incluyendo dev)
uv sync --extra dev

# 2. Generar datos de ejemplo (AAPL, MSFT, GOOGL)
uv run python -c "
from src.financial_api.data import generate_sample_data, save_raw_data, save_processed_data
from src.financial_api.features import create_features
for ticker in ['AAPL', 'MSFT', 'GOOGL']:
    df = generate_sample_data(ticker)
    save_raw_data(df, ticker, '5y')
    df_processed = create_features(df)
    save_processed_data(df_processed, ticker)
    print(f'✓ Datos generados para {ticker}')
"

# 3. Entrenar los 3 modelos para un ticker
uv run python -m src.financial_api.train --ticker AAPL --params params.yaml

# 4. Ejecutar tests
uv run pytest tests/ -v

# 5. Iniciar API en modo desarrollo
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 6. Ver documentación Swagger
open http://localhost:8000/docs
```

## Uso

### 1. Obtener datos de mercado

```bash
http://localhost:8000/market-data/AAPL/5y
```

### 2. Entrenar modelo

```bash
uv run python -m src.financial_api.train --ticker AAPL --params params.yaml
```

### 3. Ver información del modelo

```bash
http://localhost:8000/predict/model/AAPL/classification
http://localhost:8000/predict/model/AAPL/regression_return
http://localhost:8000/predict/model/AAPL/regression_volatility
```

## Arquitectura del Modelo

### 3 Modelos de Machine Learning

El proyecto implementa **3 modelos separados** usando **RandomForest** para diferentes tareas de predicción financiera:

#### 1. Modelo de Clasificación (Dirección)
- **Algoritmo**: `RandomForestClassifier`
- **Target**: `Target_Direction_t1` (1 si el precio sube mañana, 0 si baja)
- **Output**: Predicción binaria (up/down) + probabilidad real
- **Métricas**: Accuracy, F1-Score
- **Archivo**: `artifacts/{ticker}_classification.joblib`

#### 2. Modelo de Regresión (Retorno)
- **Algoritmo**: `RandomForestRegressor`
- **Target**: `Target_Return_t1` (retorno porcentual del día siguiente)
- **Output**: Retorno porcentual predicho + precio predicho
- **Métricas**: MAE, RMSE, R²
- **Archivo**: `artifacts/{ticker}_regression_return.joblib`

#### 3. Modelo de Regresión (Volatilidad)
- **Algoritmo**: `RandomForestRegressor`
- **Target**: `Target_Volatility_t1` (volatilidad de los próximos 7 días)
- **Output**: Volatilidad predicha
- **Métricas**: MAE, RMSE, R²
- **Archivo**: `artifacts/{ticker}_regression_volatility.joblib`

### Características del Pipeline

✅ **Target Leakage Corregido**: Los targets usan datos del día siguiente (t+1)
✅ **Features Temporales**: Solo se usan features disponibles ANTES de la predicción
✅ **Probabilidad Real**: La probabilidad viene de `predict_proba()` del modelo
✅ **Validación Temporal**: Split train/test respeta el orden temporal
✅ **Pipeline Completo**: Imputer + Scaler + RandomForest

## Features e Ingeniería de Características

### Features Disponibles

El modelo utiliza las siguientes features calculadas a partir de los datos históricos:

| Feature | Descripción | Ventana |
|---------|-------------|---------|
| `MA_7` | Media móvil de 7 días | 7 días |
| `MA_30` | Media móvil de 30 días | 30 días |
| `Volatility_7` | Desviación estándar de 7 días | 7 días |
| `Return_1d` | Retorno porcentual de 1 día | 1 día |
| `Return_7d` | Retorno porcentual de 7 días | 7 días |
| `Lag_1` | Precio de cierre de hace 1 día | 1 día |
| `Lag_3` | Precio de cierre de hace 3 días | 3 días |
| `Lag_5` | Precio de cierre de hace 5 días | 5 días |
| `Lag_7` | Precio de cierre de hace 7 días | 7 días |
| `Volume` | Volumen de trading | - |

### Targets (Variables Objetivo)

Los targets se calculan usando datos del **día siguiente (t+1)**:

| Target | Descripción | Fórmula |
|--------|-------------|---------|
| `Target_Direction_t1` | Dirección del precio mañana | 1 si Close(t+1) > Close(t), 0 si no |
| `Target_Return_t1` | Retorno porcentual mañana | (Close(t+1) - Close(t)) / Close(t) |
| `Target_Volatility_t1` | Volatilidad próxima 7 días | StdDev de retornos de 7 días |

### Features Excluidas

Las siguientes columnas **NO** se usan como features porque no están disponibles antes de la predicción:

- `Open`: No se conoce hasta que abre el mercado
- `High`: No se conoce hasta que cierra el mercado
- `Low`: No se conoce hasta que cierra el mercado
- `Close`: Es el target que queremos predecir

## Configuración (params.yaml)

El archivo `params.yaml` contiene todos los parámetros de configuración del modelo:

```yaml
# Configuración de datos
data:
  raw_dir: "data/raw"              # Directorio de datos crudos
  processed_dir: "data/processed"  # Directorio de datos procesados

# Configuración del modelo
model:
  random_state: 42      # Semilla para reproducibilidad
  n_estimators: 100     # Número de árboles en el bosque
  max_depth: 10         # Profundidad máxima de los árboles

# Configuración del split train/test
split:
  test_size: 0.2        # 20% de los datos para test

# Configuración de MLflow
mlflow:
  tracking_uri: "sqlite:///mlruns/mlflow.db"  # Base de datos de MLflow
  experiment_name: "stock_price_prediction"   # Nombre del experimento
```

### Parámetros Ajustables

| Parámetro | Descripción | Valor por Defecto | Rango Recomendado |
|-----------|-------------|-------------------|-------------------|
| `n_estimators` | Número de árboles | 100 | 50-500 |
| `max_depth` | Profundidad máxima | 10 | 5-20 |
| `random_state` | Semilla aleatoria | 42 | Cualquier entero |
| `test_size` | Proporción de test | 0.2 | 0.1-0.3 |

### Ajustar Hiperparámetros

Para ajustar los hiperparámetros, edita `params.yaml`:

```yaml
model:
  n_estimators: 200  # Más árboles = mejor rendimiento pero más lento
  max_depth: 15      # Más profundidad = más complejo
```

Luego reentrena el modelo:

```bash
uv run python -m src.financial_api.train --ticker AAPL --params params.yaml
```

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
gcloud artifacts repositories create mlops-mcdatos-usantoto \
  --repository-format=docker \
  --location=us-central1
```

**3. Configurar Workload Identity Federation:**
```bash
# Crear service account
gcloud iam service-accounts create fastapi-finanzas \
  --display-name="FastAPI Finanzas SA"

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
  --attribute-condition="assertion.repository=='JuSeUlloa/mlops_mcdatos_usantoto'"
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

La service account utilizada por GitHub Actions requiere los siguientes permisos:

#### APIs Habilitadas

| API | ID | Propósito |
|-----|-----|-----------|
| Cloud Run Admin API | `run.googleapis.com` | Desplegar y gestionar servicios Cloud Run |
| Artifact Registry API | `artifactregistry.googleapis.com` | Almacenar imágenes Docker |
| IAM Credentials API | `iamcredentials.googleapis.com` | Generar credenciales para Workload Identity |
| Security Token Service API | `sts.googleapis.com` | Intercambiar tokens OIDC |

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
docker pull us-central1-docker.pkg.dev/PROJECT_ID/mlops-mcdatos-usantoto/fastapi-finanzas:latest
```

## Tecnologías

- **Framework**: FastAPI
- **Servidor**: Uvicorn
- **Datos**: yfinance, pandas
- **Visualización**: matplotlib
- **ML**: scikit-learn
- **Tracking**: MLflow
- **Contenedores**: Docker
- **CI/CD**: GitHub Actions
- **Cloud**: Google Cloud Platform (Cloud Run, Artifact Registry)
- **Autenticación**: Workload Identity Federation

## Notas

- La predicción estadística usa un modelo simple basado en media y desviación estándar
- La predicción ML usa RandomForest con features de ingeniería (MAs, volatilidad, retornos, lags)
- Los gráficos se generan dinámicamente con matplotlib
- El servidor usa backend "Agg" para evitar problemas con GUI
- Los períodos se normalizan automáticamente para mejor visualización
- La API funciona offline usando datos cacheados en `data/`

## 

Actividad #2 API REST MLOps - Universidad de Santo Tomás

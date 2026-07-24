# Team 

## Miembros del Equipo

### Yeison David Toro
- **GitHub**: [@YEISON-TORO11](https://github.com/YEISON-TORO11)
- **Roles**:
  - Desarrollo de modelos de aprendizaje automático
  - Disponibilidad y preparación de datos
  - Desarrollo e implementación de pipelines de MLOps

### Juan Sebastian Ulloa
- **GitHub**: [@JuSeUlloa](https://github.com/JuSeUlloa)
- **Roles**:
  - Desarrollo de APIs para la implementación de modelos en producción
  - Desarrollo e implementación de pipelines de MLOps
  - Automatización de procesos de entrenamiento
  - Integración continua y despliegue continuo (CI/CD)
  - Monitoreo y mantenimiento de modelos en producción

## Tecnologías Utilizadas

- **Backend**: FastAPI, Uvicorn
- **ML**: scikit-learn, pandas, numpy
- **Datos**: yfinance
- **Tracking**: MLflow
- **Despliegue**: Docker, Google Cloud Run
- **CI/CD**: GitHub Actions

## Estructura del Proyecto

```
actividad2-fastapi-finanzas/
├── data/                    # Datos históricos
│   ├── raw/                # Datos crudos de Yahoo Finance
│   └── processed/          # Datos procesados con features
├── src/
│   └── financial_api/      # Paquete principal
│       ├── api.py          # Aplicación FastAPI
│       ├── data.py         # Descarga y procesamiento de datos
│       ├── features.py     # Ingeniería de features
│       ├── train.py        # Entrenamiento del modelo
│       ├── predict.py      # Servicio de predicción ML
│       ├── entities/       # Modelos Pydantic (schemas)
│       │   └── prediction.py
│       ├── routes/         # Endpoints de la API
│       │   ├── charts.py
│       │   ├── forecast.py
│       │   ├── market_data.py
│       │   └── predict.py
│       └── services/       # Lógica de negocio
│           ├── yahoo_services.py
│           └── obtain_forecast.py
├── artifacts/              # Modelos entrenados
├── tests/                  # Tests unitarios
├── reports/                # Métricas y gráficos
├── Dockerfile              # Configuración Docker
├── pyproject.toml          # Dependencias
└── README.md               # Documentación
```

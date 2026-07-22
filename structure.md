# Estructura del Proyecto y Configuración del Entorno

## Tabla de Contenidos
1. [Instalación de uv](#instalación-de-uv)
2. [Configuración del Proyecto](#configuración-del-proyecto)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Ejecución del Proyecto](#ejecución-del-proyecto)
5. [Actividad 2: FastAPI Finanzas](#actividad-2-fastapi-finanzas)
6. [Estructura de Directorios](#estructura-de-directorios)

---

## Instalación de uv

`uv` es un gestor de paquetes y entornos virtuales extremadamente rápido para Python, desarollado en lenguaje de programacio Rust.

### Windows

#### Opción 1: Usando pip ( debe contar con )
```cmd
pip install uv
```

#### Opción 2: Descarga directa
1. Descarga el ejecutable desde [GitHub](https://github.com/astral-sh/uv/releases)
2. Agrega el directorio de descarga a tu variable de entorno `PATH`

#### Verificar instalación en Windows
```cmd
uv --version
```

### macOS

#### Opción 1: Homebrew 
```bash
brew install uv
```

#### Opción 2: Script de instalación
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Opción 3: Usando pip (debe tener instalado Python)
```bash
pip install uv
```

#### Verificar instalación en macOS
```bash
uv --version
```

### Linux

#### Opción 1: Script de instalación (Recomendado)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Opción 2: Usando pip
```bash
pip install uv
```

#### Opción 3: Desde código fuente
```bash
git clone https://github.com/astral-sh/uv.git
cd uv
cargo build --release
sudo cp target/release/uv /usr/local/bin/
```

#### Verificar instalación en Linux
```bash
uv --version
```

## Configuración del Proyecto

### 1. Navegar al Directorio del Proyecto
```bash
cd actividad1-mlops-openrate
```

### 3. Configurar Versión de Python

#### Crear entorno virtual
```bash
uv venv
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

---

## Instalación de Dependencias

### Dependencias Principales

#### Instalar todas las dependencias del proyecto
```bash
uv sync
```

#### Instalar dependencias específicas
```bash
uv add numpy pandas matplotlib seaborn mlflow dvc scikit-learn joblib 
```

### Dependencias de Desarrollo

#### Instalar herramientas de desarrollo
```bash
uv add --dev ## dependecias
```

### Verificar Instalación

#### Listar paquetes instalados
```bash
uv pip list
```

#### Ver árbol de dependencias
```bash
uv pip tree
```

---

## Ejecución del Proyecto

### Opción 1: Usando uv run (Recomendado)
```bash
uv run src/main.py
```

### Opción 2: Con entorno virtual activado
```bash
python src/main.py
```

### Opción 3: Especificando el intérprete
```bash
uv run --python 3.14 src/main.py
```

### Opción 4: Usando Make (Recomendado)
```bash
make run
```

---

## Comandos Make

El proyecto incluye un `Makefile` para centralizar los comandos más utilizados.

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `make install` | Instalar/sincronizar dependencias |
| `make test` | Ejecutar todas las pruebas |
| `make test-unit` | Ejecutar solo pruebas unitarias |
| `make test-integration` | Ejecutar solo pruebas de integración |
| `make run` | Ejecutar el script principal |
| `make clean` | Limpiar archivos de cache |

### Ejemplos de Uso

```bash
# Instalar dependencias
make install

# Ejecutar todas las pruebas
make test

# Ejecutar solo pruebas unitarias
make test-unit

# Ejecutar el proyecto
make run

# Limpiar archivos temporales
make clean
```

---

## Actividad 2: FastAPI Finanzas

### Configuración del Proyecto FastAPI

#### 1. Navegar al Directorio del Proyecto
```bash
cd actividad2-fastapi-finanzas
```

#### 2. Sincronizar Dependencias
```bash
uv sync
```

#### 3. Solución de Problemas de Imports

Si al ejecutar `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000` obtienes el error:
```
ModuleNotFoundError: No module named 'routes'
```

**Causa:** Los archivos `__init__.py` faltan en los directorios `src/`, `src/routes/` y `src/services/`, y los imports son absolutos en lugar de relativos.

**Solución:**

##### Paso 1: Crear archivos `__init__.py`
```bash
touch src/__init__.py
touch src/routes/__init__.py
touch src/services/__init__.py
```

##### Paso 2: Cambiar imports a relativos en `src/main.py`
```python
# Cambiar de:
from routes.charts import router as charts_router
from routes.forecast import router as forecast_7d

# A:
from .routes.charts import router as charts_router
from .routes.forecast import router as forecast_7d
```

##### Paso 3: Cambiar imports a relativos en `src/routes/charts.py`
```python
# Cambiar de:
from services.yahoo_services import build_history_chart_png

# A:
from ..services.yahoo_services import build_history_chart_png
```

##### Paso 4: Cambiar imports a relativos en `src/routes/forecast.py`
```python
# Cambiar de:
from services.obtnain_forecast import model_forecast
from services.yahoo_services import get_one_year_history

# A:
from ..services.obtnain_forecast import model_forecast
from ..services.yahoo_services import get_one_year_history
```

#### 4. Ejecutar el Servidor FastAPI
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Endpoints Disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de estado de la API |
| GET | `/health` | Verificación de salud |
| GET | `/charts/history/{ticker}` | Gráfico PNG de precios históricos (1 año) |
| GET | `/forecast/forecast/{ticker}` | Predicción de 7 días |

#### 6. Probar la API

Puedes acceder a la documentación interactiva en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Ejemplos de uso:
```bash
# Verificar que la API está corriendo
curl http://localhost:8000/

# Obtener gráfico de Apple (1 año)
curl http://localhost:8000/charts/history/AAPL --output aapl_chart.png

# Obtener predicción de 7 días para Microsoft
curl http://localhost:8000/forecast/forecast/MSFT
```

---

## Estructura de Directorios

mkdir models
mkdir outputs
mkdir mlruns

```
mlops_mcdatos_usantoto/
├── README.md                           # Documentación principal del repositorio
├── structure.md                        # Este archivo - Guía de configuración
├── .gitignore                          # Archivos ignorados por git
│
├── actividad1-mlops-openrate/          # Directorio de la actividad 1
│   ├── README.md                       # Documentación específica de la actividad
│   ├── pyproject.toml                  # Configuración del proyecto (uv)
│   ├── uv.lock                         # Archivo lock de dependencias
│   ├── Makefile                        # Comandos centralizados del proyecto
│   ├── .python-version                 # Versión de Python fijada
│   ├── .venv/                          # Entorno virtual (no versionado)
│   │
│   ├── data/                           # Directorio de datos
│   │   └── training_data.csv           # Dataset generado (1500 registros)
│   │
│   ├── src/                            # Código fuente
│   │   └── main.py                     # Script principal
│   │
│   └── tests/                          # Pruebas
│       ├── conftest.py                 # Fixtures compartidos
│       ├── unit/                       # Pruebas unitarias
│       │   └── test_main.py
│       └── integration/                # Pruebas de integración
│           └── test_integration.py
│
└── actividad2-fastapi-finanzas/        # Directorio de la actividad 2 (FastAPI)
    ├── README.md                       # Documentación de la actividad (vacío)
    ├── pyproject.toml                  # Configuración del proyecto (uv)
    ├── uv.lock                         # Archivo lock de dependencias
    ├── .python-version                 # Versión de Python fijada (3.14)
    ├── .venv/                          # Entorno virtual (no versionado)
    │
    └── src/                            # Código fuente
        ├── __init__.py                 # Init del paquete src
        ├── main.py                     # Aplicación FastAPI principal
        │
        ├── routes/                     # Rutas de la API
        │   ├── __init__.py             # Init del paquete routes
        │   ├── charts.py               # Endpoint para gráficos históricos
        │   └── forecast.py             # Endpoint para predicciones
        │
        └── services/                   # Lógica de negocio
            ├── __init__.py             # Init del paquete services
            ├── yahoo_services.py       # Servicio para datos de Yahoo Finance
            └── obtnain_forecast.py     # Servicio de predicción (typo en nombre)
```

### Descripción de Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `pyproject.toml` | Configuración del proyecto, dependencias y metadatos |
| `uv.lock` | Versiones exactas de todas las dependencias instaladas |
| `Makefile` | Comandos centralizados (install, test, run, clean) |
| `.python-version` | Versión específica de Python para el proyecto |
| `.venv/` | Entorno virtual aislado (no debe versionarse) |
| `training_data.csv` | Dataset sintético generado para entrenamiento |
| `main.py` | Script principal del proyecto |
| `tests/` | Directorio de pruebas unitarias y de integración |

---

## Comandos Útiles de uv

### Gestión de Proyectos
```bash
uv init                           # Inicializar nuevo proyecto
uv add <paquete>                  # Agregar dependencia
uv remove <paquete>               # Eliminar dependencia
uv sync                           # Sincronizar entorno con dependencias
uv lock                           # Actualizar archivo lock
```

### Gestión de Entornos
```bash
uv venv                           # Crear entorno virtual
uv run <comando>                  # Ejecutar comando en entorno virtual
uv python install <versión>       # Instalar versión de Python
uv python pin <versión>           # Fijar versión de Python
```

### Gestión de Dependencias
```bash
uv pip list                       # Listar paquetes instalados
uv pip tree                       # Mostrar árbol de dependencias
uv pip show <paquete>             # Mostrar información de paquete
uv pip install <paquete>          # Instalar paquete específico
```

### Ejecución de Scripts
```bash
uv run script.py                  # Ejecutar script Python
uv run --python 3.12 script.py    # Ejecutar con versión específica
uv run pytest                     # Ejecutar tests
```

---

## Solución de Problemas

### Error: `uv: command not found`

**Causa:** `uv` no está en el PATH

**Solución:**
```bash
# Agregar al PATH temporalmente
export PATH="$HOME/.local/bin:$PATH"

# Para hacer permanente, agregar a ~/.bashrc o ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Error: `ModuleNotFoundError`

**Causa:** Dependencias no instaladas

**Solución:**
```bash
uv sync
# o
uv add numpy pandas
```

### Error: Versión de Python incompatible

**Causa:** Versión de Python no soportada

**Solución:**
```bash
uv python install 3.12
uv python pin 3.12
uv sync
```

### Error: Permisos denegados en Linux/macOS

**Causa:** Permisos insuficientes

**Solución:**
```bash
chmod +x ~/.local/bin/uv
# o reinstalar con permisos adecuados
```

### Error: Firewall bloquea descarga en Windows

**Causa:** Firewall corporativo bloquea descargas

**Solución:**
```cmd
# Usar proxy si está disponible
set HTTPS_PROXY=http://proxy.empresa.com:puerto
uv sync
```

---

## Mejores Prácticas

### 1. Versionamiento
- Siempre usar `uv.lock` para garantizar instalaciones reproducibles
- No versionar el directorio `.venv/`
- Mantener `pyproject.toml` actualizado

### 2. Entornos Virtuales
- Usar entornos virtuales para cada proyecto
- Activar entorno antes de ejecutar scripts
- Usar `uv run` para evitar activación manual

### 3. Dependencias
- Especificar versiones mínimas en `pyproject.toml`
- Usar `uv sync` en lugar de `uv pip install`
- Separar dependencias de desarrollo con `--dev`

### 4. Colaboración
- Compartir `pyproject.toml` y `uv.lock`
- Documentar versión de Python requerida
- Incluir instrucciones de instalación en README

---

## Referencias

- [Documentación oficial de uv](https://docs.astral.sh/uv/)
- [Repositorio de uv en GitHub](https://github.com/astral-sh/uv)
- [Guía de migración desde pip a uv](https://docs.astral.sh/uv/guides/migrate-pip/)
- [Mejores prácticas de Python](https://docs.python-guide.org/)


# Estructura del Proyecto y Configuración del Entorno

## Tabla de Contenidos
1. [Instalación de uv](#instalación-de-uv)
2. [Configuración del Proyecto](#configuración-del-proyecto)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Ejecución del Proyecto](#ejecución-del-proyecto)
5. [Estructura de Directorios](#estructura-de-directorios)

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
uv add numpy pandas scikit-learn matplotlib seaborn 
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

---

## Estructura de Directorios

mkdir models
mkdir outputs
mkdir mlruns

```
mlops_mcdatos_usantoto/
├── README.md                           # Documentación principal del repositorio

├── .gitignore                          # Archivos ignorados por git
│
└── actividad1-mlops-openrate/          # Directorio de la actividad
    ├── README.md                       # Documentación específica de la actividad
    ├── pyproject.toml                  # Configuración del proyecto (uv)
    ├── uv.lock                         # Archivo lock de dependencias
    ├── .python-version                 # Versión de Python fijada
    ├── .venv/                          # Entorno virtual (no versionado)
    │
    ├── data/                           # Directorio de datos
    │   └── training_data.csv           # Dataset generado (1500 registros)
    │
    └── src/                            # Código fuente
        └── generate_data.py            # Script de generación de datos
    ├── structure.md                    # Este archivo - Guía de configuración
```

### Descripción de Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `pyproject.toml` | Configuración del proyecto, dependencias y metadatos |
| `uv.lock` | Versiones exactas de todas las dependencias instaladas |
| `.python-version` | Versión específica de Python para el proyecto |
| `.venv/` | Entorno virtual aislado (no debe versionarse) |
| `training_data.csv` | Dataset sintético generado para entrenamiento |
| `generate_data.py` | Script que genera datos sintéticos realistas |

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


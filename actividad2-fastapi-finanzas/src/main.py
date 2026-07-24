import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    from .financial_api import app
    logger.info("✅ Aplicación FastAPI cargada exitosamente")
except Exception as e:
    logger.error(f"❌ Error al cargar la aplicación: {e}", exc_info=True)
    raise

__all__ = ["app"]


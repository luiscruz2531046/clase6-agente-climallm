import os
from pathlib import Path


def _load_dotenv() -> None:
    """Carga variables desde un archivo .env simple, sin dependencia extra."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10

# Configuracion opcional para usar un LLM.
# Puedes activarlo con variables de entorno o con un archivo .env.
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").strip().lower() in {"true", "1", "yes", "si", "sí"}
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")

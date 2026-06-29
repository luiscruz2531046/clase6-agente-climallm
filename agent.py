import re

from llm_client import LLMClient
from tools.weather_tool import WeatherTool
from utils.errors import ValidationError
from utils.validators import validate_city_name


QUESTION_WORDS = (
    "clima",
    "temperatura",
    "llueve",
    "lluvia",
    "frio",
    "frío",
    "calor",
    "como",
    "cómo",
    "esta",
    "está",
    "hoy",
    "mañana",
    "paraguas",
    "chamarra",
    "abrigo",
    "viento",
    "humedad",
)

TRAILING_WORDS = (
    "hoy",
    "mañana",
    "ahorita",
    "actualmente",
    "por favor",
    "favor",
    "actual",
)


def extract_city_by_rules(user_input: str) -> str | None:
    """Extrae una ciudad con reglas simples cuando el LLM esta apagado.

    Ejemplos soportados:
    - como esta el clima en Puebla hoy -> Puebla
    - clima de Tulancingo -> Tulancingo
    - temperatura para Ciudad de Mexico hoy -> Ciudad de Mexico
    - necesito paraguas en Puebla -> Puebla
    """
    text = " ".join(user_input.strip().split())
    if not text:
        return None

    patterns = (
        r"\ben\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ .-]+)",
        r"\bde\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ .-]+)",
        r"\bpara\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ .-]+)",
    )

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue

        city = match.group(1).strip(" .,-¿?¡!")

        # Quita palabras de tiempo o cortesía al final.
        changed = True
        while changed:
            changed = False
            lower_city = city.lower()

            for word in TRAILING_WORDS:
                suffix = " " + word
                if lower_city.endswith(suffix):
                    city = city[: -len(suffix)].strip(" .,-¿?¡!")
                    changed = True
                    break

        if city:
            return city

    return None


class WeatherAgent:
    """Agente con percepcion, decision y accion apoyado opcionalmente por un LLM."""

    def __init__(
        self,
        tool: WeatherTool | None = None,
        llm: LLMClient | None = None,
    ) -> None:
        self.tool = tool or WeatherTool()
        self.llm = llm or LLMClient.from_env()
        self.selected_tool = "weather_tool"

    def perceive(self, user_input: str) -> str:
        """Recibe la entrada del usuario y extrae la ciudad."""
        extracted_city = self.llm.extract_city(user_input)

        if not extracted_city:
            extracted_city = extract_city_by_rules(user_input)

        if extracted_city:
            return validate_city_name(extracted_city)

        normalized_input = user_input.strip().lower()
        looks_like_question = any(word in normalized_input for word in QUESTION_WORDS)

        if looks_like_question:
            raise ValidationError(
                "No detecte una ciudad. Escribe algo como: 'como esta el clima en Puebla hoy'."
            )

        return validate_city_name(user_input)

    def decide(self, city: str) -> str:
        """Decide que herramienta usar."""
        if not city:
            raise ValidationError("La ciudad no puede estar vacia.")

        self.selected_tool = "weather_tool"
        return city

    def act(self, city: str, user_input: str) -> str:
        """Consulta la API de clima y construye el reporte final."""
        location = self.tool.get_coordinates(city)
        weather = self.tool.get_current_weather(location.latitude, location.longitude)
        fallback_report = self.tool.build_report(location, weather)

        return self.llm.build_weather_report(
            location=location,
            weather=weather,
            fallback_report=fallback_report,
            user_input=user_input,
        )

    def run(self, user_input: str) -> str:
        """Ejecuta el flujo completo del agente."""
        city = self.perceive(user_input)
        city = self.decide(city)
        return self.act(city, user_input)
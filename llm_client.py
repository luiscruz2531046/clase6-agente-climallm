import json
import re
from typing import Any

from config import LLM_API_KEY, LLM_BASE_URL, LLM_ENABLED, LLM_MODEL
from models.weather_models import Location, WeatherData


class LLMClient:
    """Cliente opcional para usar un LLM dentro del agente.

    El agente sigue usando la herramienta de clima para obtener datos reales.
    El LLM se usa para:
    1. Extraer la ciudad desde una frase natural del usuario.
    2. Entender la intención de la pregunta.
    3. Redactar un reporte coherente con lo que el usuario preguntó.
    """

    def __init__(
        self,
        enabled: bool = LLM_ENABLED,
        model: str = LLM_MODEL,
        api_key: str | None = LLM_API_KEY,
        base_url: str | None = LLM_BASE_URL,
    ) -> None:
        self.enabled = enabled
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._client: Any | None = None

    @classmethod
    def from_env(cls) -> "LLMClient":
        """Crea el cliente usando variables de entorno."""
        return cls()

    def extract_city(self, user_input: str) -> str | None:
        """Extrae el nombre de la ciudad desde una pregunta natural."""
        if not self.enabled:
            return None

        prompt = f"""
Extrae solamente la ciudad mencionada en la pregunta del usuario.

Reglas:
- Responde únicamente en JSON válido.
- No uses markdown.
- No expliques nada.
- Si no hay ciudad clara, responde {{"city": ""}}.
- Si el usuario pregunta "¿necesito paraguas en Puebla?", la ciudad es "Puebla".
- Si el usuario pregunta "cómo está el clima en Tulancingo hoy", la ciudad es "Tulancingo".


Formato exacto:
{{"city": "nombre de la ciudad"}}

Pregunta del usuario:
{user_input}
""".strip()

        try:
            response_text = self._generate_text(prompt)
            data = self._parse_json(response_text)
            city = str(data.get("city", "")).strip()
            return city or None
        except Exception as error:
            print(f"[Aviso LLM] No se pudo usar el modelo para extraer la ciudad: {error}")
            return None

    def build_weather_report(
        self,
        location: Location,
        weather: WeatherData,
        fallback_report: str,
        user_input: str = "",
    ) -> str:
        """Genera un reporte final con lenguaje natural usando datos reales."""
        if not self.enabled:
            return fallback_report

        prompt = f"""
Eres un asistente de clima dentro de un agente.

Tu tarea es responder DIRECTAMENTE la pregunta del usuario usando solamente los datos reales entregados por la herramienta de clima.

Pregunta original del usuario:
{user_input}

Datos reales consultados:
- Ciudad: {location.name}
- Pais/Region: {location.country}
- Temperatura: {weather.temperature:.1f} °C
- Humedad relativa: {weather.humidity:.0f} %
- Velocidad del viento: {weather.wind_speed:.1f} km/h
- Precipitacion: {weather.precipitation:.1f} mm
- Hora de medicion: {weather.time}

Reglas obligatorias:
- No inventes datos.
- No contradigas la precipitacion, temperatura, humedad ni viento.
- Si el usuario pregunta por paraguas, responde primero si lo necesita o no.
- Si la precipitacion es 0.0 mm, indica que no parece necesario llevar paraguas en este momento.
- Si el usuario pregunta por mañana, futuro o pronóstico, aclara que los datos disponibles son del clima actual.
- No uses la precipitación actual para afirmar si lloverá mañana.
- Si pregunta "¿lloverá mañana?", responde que no puedes confirmarlo con estos datos actuales y que se necesita consultar un pronóstico.
- Si el usuario pregunta si hace frio, calor o si debe llevar chamarra, usa la temperatura.
- Si el usuario pregunta algo general, da un resumen breve del clima.
- La recomendacion debe ser coherente con los datos.
- No digas "ropa ligera" si la temperatura es fresca o fria.
- Responde en español, claro y natural.
- Maximo 120 palabras.

Respuesta final:
""".strip()

        try:
            return self._generate_text(prompt).strip()
        except Exception as error:
            print(f"[Aviso LLM] No se pudo generar el reporte con LLM: {error}")
            return fallback_report

    def _generate_text(self, prompt: str) -> str:
        """Llama al modelo configurado usando Chat Completions."""
        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente de clima. "
                        "Responde de forma breve, clara, útil y siguiendo exactamente las instrucciones. "
                        "No inventes informacion."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=250,
        )

        content = response.choices[0].message.content
        return str(content or "")

    def _get_client(self) -> Any:
        """Carga el SDK solamente cuando se necesita el LLM."""
        if self._client is not None:
            return self._client

        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError(
                "Falta instalar la dependencia 'openai'. Ejecuta: pip install openai"
            ) from error

        kwargs: dict[str, str] = {}

        if self.api_key:
            kwargs["api_key"] = self.api_key
        elif self.base_url:
            kwargs["api_key"] = "lm-studio"

        if self.base_url:
            kwargs["base_url"] = self.base_url

        self._client = OpenAI(**kwargs)
        return self._client

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        """Intenta convertir la respuesta del LLM a JSON."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return {}
            return json.loads(match.group(0))
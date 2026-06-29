import requests

from config import FORECAST_URL, GEOCODING_URL, REQUEST_TIMEOUT
from models.weather_models import Location, WeatherData
from utils.errors import CityNotFoundError, WeatherAPIError


class WeatherTool:
    """Herramienta encargada de consultar Open-Meteo."""

    def __init__(
        self,
        geocoding_url: str = GEOCODING_URL,
        forecast_url: str = FORECAST_URL,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        self.geocoding_url = geocoding_url
        self.forecast_url = forecast_url
        self.timeout = timeout

    def get_coordinates(self, city: str) -> Location:
        """Busca una ciudad y devuelve sus coordenadas."""
        params = {
            "name": city,
            "count": 1,
            "language": "es",
            "format": "json",
        }
        data = self._make_request(self.geocoding_url, params)
        results = data.get("results")

        if not isinstance(results, list) or not results:
            raise CityNotFoundError(f"No se encontro informacion para '{city}'.")

        location_data = results[0]

        try:
            return Location(
                name=str(location_data["name"]),
                country=self._build_country_label(location_data),
                latitude=float(location_data["latitude"]),
                longitude=float(location_data["longitude"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise WeatherAPIError(
                "La API devolvio datos de ubicacion incompletos o invalidos."
            ) from error

    def get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Consulta el clima actual para unas coordenadas."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "wind_speed_10m,precipitation"
            ),
            "timezone": "auto",
        }
        data = self._make_request(self.forecast_url, params)
        current = data.get("current")

        if not isinstance(current, dict):
            raise WeatherAPIError("La API devolvio una respuesta de clima invalida.")

        required_fields = {
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "precipitation",
        }

        if not required_fields.issubset(current):
            raise WeatherAPIError("Faltan datos obligatorios en la respuesta del clima.")

        try:
            return WeatherData(
                time=str(current["time"]),
                temperature=float(current["temperature_2m"]),
                humidity=float(current["relative_humidity_2m"]),
                wind_speed=float(current["wind_speed_10m"]),
                precipitation=float(current["precipitation"]),
            )
        except (TypeError, ValueError) as error:
            raise WeatherAPIError("Los valores del clima tienen un formato invalido.") from error

    def build_report(self, location: Location, weather: WeatherData) -> str:
        """Construye un reporte de texto para el usuario."""
        lines = [
            f"Ciudad consultada: {location.name}",
            f"Pais/Region: {location.country}",
            f"Temperatura actual: {weather.temperature:.1f} C",
            f"Humedad relativa: {weather.humidity:.0f} %",
            f"Velocidad del viento: {weather.wind_speed:.1f} km/h",
            f"Precipitacion: {weather.precipitation:.1f} mm",
            f"Hora de la medicion: {weather.time}",
            f"Interpretacion: {self._interpret_weather(weather)}",
        ]
        return "\n".join(lines)

    def _make_request(self, url: str, params: dict[str, object]) -> dict:
        """Realiza una peticion HTTP con manejo basico de errores."""
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise WeatherAPIError("La API devolvio una estructura JSON invalida.")
            return data
        except requests.exceptions.Timeout as error:
            raise WeatherAPIError(
                "La consulta tardo demasiado tiempo. Intenta nuevamente."
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise WeatherAPIError(
                "No fue posible conectarse con el servicio de clima."
            ) from error
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response else "desconocido"
            raise WeatherAPIError(
                f"El servicio de clima respondio con error HTTP {status_code}."
            ) from error
        except requests.exceptions.RequestException as error:
            raise WeatherAPIError("Ocurrio un error al consultar la API del clima.") from error
        except ValueError as error:
            raise WeatherAPIError("La API devolvio un JSON invalido.") from error

    @staticmethod
    def _build_country_label(location_data: dict[str, object]) -> str:
        country = str(location_data.get("country", "")).strip()
        region = str(location_data.get("admin1", "")).strip()

        if country and region and country.lower() != region.lower():
            return f"{country}, {region}"
        if country:
            return country
        if region:
            return region
        return "No disponible"

    @staticmethod
    def _interpret_weather(weather: WeatherData) -> str:
        if weather.precipitation > 0:
            return "Hay posibilidad de lluvia o lluvia ligera en este momento."
        if weather.temperature >= 30:
            return "El clima es muy caluroso."
        if weather.temperature >= 24:
            return "El clima es calido."
        if weather.temperature >= 18:
            return "El clima es templado."
        if weather.temperature >= 10:
            return "El clima es fresco."
        return "El clima es frio."

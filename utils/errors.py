class ValidationError(Exception):
    """Error de validacion de datos de entrada."""


class WeatherAPIError(Exception):
    """Error al consultar o procesar la API de clima."""


class CityNotFoundError(Exception):
    """Error cuando la ciudad no existe o no fue encontrada."""

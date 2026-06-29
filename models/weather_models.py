from dataclasses import dataclass


@dataclass
class Location:
    name: str
    country: str
    latitude: float
    longitude: float


@dataclass
class WeatherData:
    time: str
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float

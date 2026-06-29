from agent import WeatherAgent
from models.weather_models import Location, WeatherData


class FakeWeatherTool:
    def __init__(self) -> None:
        self.received_city = ""
        self.received_coordinates: tuple[float, float] | None = None

    def get_coordinates(self, city: str) -> Location:
        self.received_city = city
        return Location(
            name="Madrid",
            country="España, Madrid",
            latitude=40.4168,
            longitude=-3.7038,
        )

    def get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        self.received_coordinates = (latitude, longitude)
        return WeatherData(
            time="2026-06-23T08:00",
            temperature=27.5,
            humidity=40.0,
            wind_speed=12.0,
            precipitation=0.0,
        )

    def build_report(self, location: Location, weather: WeatherData) -> str:
        return (
            f"{location.name} - {location.country} - "
            f"{weather.temperature} - {weather.time}"
        )


def test_agent_run_with_mock_tool() -> None:
    fake_tool = FakeWeatherTool()
    agent = WeatherAgent(tool=fake_tool)

    result = agent.run("  Madrid   ")

    assert result == "Madrid - España, Madrid - 27.5 - 2026-06-23T08:00"
    assert fake_tool.received_city == "Madrid"
    assert fake_tool.received_coordinates == (40.4168, -3.7038)


def test_agent_extracts_city_from_question_without_llm() -> None:
    fake_tool = FakeWeatherTool()
    agent = WeatherAgent(tool=fake_tool)

    result = agent.run("como esta el clima en Puebla hoy")

    assert result == "Madrid - España, Madrid - 27.5 - 2026-06-23T08:00"
    assert fake_tool.received_city == "Puebla"


def test_agent_extracts_city_after_de_without_llm() -> None:
    fake_tool = FakeWeatherTool()
    agent = WeatherAgent(tool=fake_tool)

    result = agent.run("temperatura de Tulancingo hoy")

    assert result == "Madrid - España, Madrid - 27.5 - 2026-06-23T08:00"
    assert fake_tool.received_city == "Tulancingo"

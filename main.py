from agent import WeatherAgent
from config import LLM_BASE_URL, LLM_ENABLED, LLM_MODEL
from utils.errors import CityNotFoundError, ValidationError, WeatherAPIError


def main() -> None:
    """Punto de entrada del programa en consola."""
    print("=== Agente de clima ===")
    print("Puedes escribir una ciudad o una pregunta, por ejemplo:")
    print("- Puebla")
    print("- como esta el clima en Puebla hoy\n")

    print(f"LLM activo: {'si' if LLM_ENABLED else 'no'}")
    if LLM_ENABLED:
        print(f"Modelo LLM: {LLM_MODEL or 'no configurado'}")
        print(f"Base URL: {LLM_BASE_URL or 'OpenAI oficial'}")
    else:
        print("Nota: el modo sin LLM sigue intentando extraer ciudades con reglas simples.")
    print()

    user_input = input("Consulta: ")
    agent = WeatherAgent()

    try:
        report = agent.run(user_input)
        print("\n=== Reporte del clima ===")
        print(report)
    except ValidationError as error:
        print(f"\nEntrada invalida: {error}")
    except CityNotFoundError as error:
        print(f"\n{error}")
    except WeatherAPIError as error:
        print(f"\nNo fue posible consultar el clima: {error}")
    except Exception as error:
        print(f"\nOcurrio un error inesperado: {error}")


if __name__ == "__main__":
    main()

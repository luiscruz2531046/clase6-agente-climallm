# Weather Agent con LLM 

Proyecto escolar en Python que consulta el clima actual de una ciudad usando la API publica de Open-Meteo. Tambien puede usar un LLM de forma opcional para entender frases naturales y redactar un reporte mas conversacional.

## Requisitos

- Python 3.11 o superior
- Conexion a internet para consultar Open-Meteo
- Opcional: API key de OpenAI o servidor local compatible, por ejemplo LM Studio

## Instalacion

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion sin LLM

Este modo conserva el comportamiento original. Solo escribe el nombre de la ciudad.

```powershell
python main.py
```

Ejemplo:

```text
Ciudad: Puebla
```

## Ejecucion con LLM usando OpenAI

En PowerShell:

```powershell
setx OPENAI_API_KEY "tu_api_key"
setx LLM_ENABLED "true"
setx LLM_MODEL "gpt-5.5"
```

Cierra y vuelve a abrir la terminal. Luego ejecuta:

```powershell
python main.py
```

Con LLM puedes escribir frases mas naturales:

```text
Ciudad: como esta el clima en Puebla hoy?
```

## Ejecucion con LLM local usando LM Studio

1. Abre LM Studio.
2. Carga un modelo.
3. Activa el servidor local en la pestana Developer.
4. Configura las variables:

```powershell
setx LLM_ENABLED "true"
setx OPENAI_BASE_URL "http://localhost:1234/v1"
setx LLM_MODEL "el_nombre_del_modelo_cargado_en_lm_studio"
```

Cierra y vuelve a abrir la terminal. Luego ejecuta:

```powershell
python main.py
```

## Arquitectura del agente

El proyecto mantiene el ciclo del agente:

- **Percepcion:** recibe el texto del usuario. Si el LLM esta activo, extrae la ciudad desde una frase natural. Si no esta activo, valida directamente el nombre de la ciudad.
- **Decision:** selecciona la herramienta de clima.
- **Accion:** consulta Open-Meteo para obtener datos reales y despues genera el reporte final.

Importante: el LLM no reemplaza a la API de clima. La API sigue siendo la fuente real de los datos. El LLM solo ayuda a interpretar la entrada y redactar la salida.

## Archivos principales

```text
weather_agent/
├── main.py
├── agent.py
├── llm_client.py
├── config.py
├── tools/
│   └── weather_tool.py
├── models/
│   └── weather_models.py
├── utils/
│   ├── validators.py
│   └── errors.py
└── tests/
```

## Pruebas

```powershell
pytest
```

Las pruebas pueden ejecutarse sin tener LLM activo porque el uso del modelo es opcional.


## Activar LLM con LM Studio usando `.env`

1. En LM Studio abre `Developer` y presiona `Start Server`.
2. Verifica que el servidor quede en `http://localhost:1234/v1`.
3. Copia `.env.example` y renómbralo a `.env`.
4. Cambia `LLM_MODEL` por el nombre exacto del modelo cargado en LM Studio.
5. Ejecuta:

```bash
python main.py
```

Al iniciar debe aparecer:

```text
LLM activo: si
Base URL: http://localhost:1234/v1
```

Si aparece `LLM activo: no`, el programa no está leyendo la configuración. Revisa que el archivo se llame exactamente `.env` y que esté en la misma carpeta que `main.py`.

Esta versión también tiene una extracción por reglas como respaldo. Aunque el LLM esté apagado, frases como `como esta el clima en Puebla hoy` deberían extraer `Puebla`.

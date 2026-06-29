# Bitácora de uso de Codex CLI

## Iteración 1

### Prompt enviado
Desarrolla un agente en Python 3.11 o superior que consulte una API pública y gratuita de clima. El proyecto debe separar la lógica del agente y la herramienta en módulos distintos, validar la ciudad ingresada, manejar errores de red, ciudades inválidas y respuestas inesperadas, usar timeout e incluir pruebas con pytest.

### Qué devolvió Codex
Codex propuso una estructura inicial con archivos separados para el agente, la herramienta de clima, configuración y pruebas. También sugirió usar la API Open-Meteo para consultar información del clima.

### Qué se conservó
Se conservó la idea de separar la lógica del agente de la herramienta y de usar una API pública de clima.

### Qué se cambió o descartó
Se reorganizó la herramienta dentro de `tools/weather_tool.py` y se agregaron módulos auxiliares para validaciones, errores personalizados y modelos de datos.

### Justificación
La separación por módulos hace que el código sea más ordenado, fácil de mantener y más sencillo de probar.

## Iteración 2

### Prompt enviado
Mejora el proyecto agregando manejo controlado de errores: ciudad vacía, ciudad inválida, ciudad no encontrada, errores HTTP, errores de red, timeout, JSON inválido y pruebas automatizadas con pytest.

### Qué devolvió Codex
Codex propuso agregar excepciones personalizadas, validaciones más estrictas y pruebas con pytest.

### Qué se conservó
Se conservaron las excepciones personalizadas, el uso de timeout y la idea de validar la estructura de la respuesta de la API.

### Qué se cambió o descartó
Se ajustaron los mensajes de error para que fueran más comprensibles para el usuario. También se usó una herramienta falsa en las pruebas para evitar depender de internet.

### Justificación
Esto mejora la confiabilidad del programa porque permite fallar de manera controlada cuando hay problemas con la entrada del usuario, la red o la API.

## Error, omisión o mejora detectada

Una omisión inicial fue confiar demasiado en que la API siempre respondería correctamente. Para corregirlo, se agregó validación del JSON, manejo de códigos HTTP, timeout y mensajes claros para el usuario.

## Mejora de confiabilidad

La confiabilidad se mejoró mediante validación de entradas, timeout, manejo de excepciones, pruebas automatizadas y separación entre agente y herramienta.
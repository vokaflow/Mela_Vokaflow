# VokaFlow Backend

Este es el backend Python para el proyecto VokaFlow, un sistema de comunicación instantánea con capacidades avanzadas de traducción y un agente de IA (Vicky) como cerebro orquestador.

## Requisitos

- Python 3.10 o superior
- Dependencias listadas en `requirements.txt`

## Instalación

1. Crea un entorno virtual:

\`\`\`bash
python -m venv venv
\`\`\`

2. Activa el entorno virtual:

- En Windows:
\`\`\`bash
venv\Scripts\activate
\`\`\`

- En macOS/Linux:
\`\`\`bash
source venv/bin/activate
\`\`\`

3. Instala las dependencias:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Ejecución

Para iniciar el servidor:

\`\`\`bash
python run_backend.py
\`\`\`

Opciones disponibles:

- `--host`: Host para el servidor (default: 0.0.0.0)
- `--port`: Puerto para el servidor (default: 5000)
- `--reload`: Activar recarga automática durante desarrollo

Ejemplo:

\`\`\`bash
python run_backend.py --host 127.0.0.1 --port 8000 --reload
\`\`\`

## Estructura del Proyecto

- `main.py`: Punto de entrada principal y definición de endpoints API
- `vicky/`: Módulos relacionados con el cerebro de Vicky
  - `brain.py`: Implementación del cerebro dual-hemisferio
- `run_backend.py`: Script para iniciar el servidor

## API Endpoints

### Vicky

- `POST /api/vicky/process`: Procesa una solicitud para Vicky
- `GET /api/vicky/status`: Obtiene el estado actual de Vicky
- `POST /api/vicky/config`: Actualiza la configuración de Vicky

### Traducción

- `POST /api/translate`: Traduce un texto de un idioma a otro
- `GET /api/translate/languages`: Obtiene la lista de idiomas soportados
- `GET /api/translate/stats`: Obtiene estadísticas de traducción

### Sistema

- `GET /`: Endpoint raíz para verificar que el servidor está funcionando
- `GET /health`: Endpoint para verificar el estado del servidor

## Conexión con el Frontend

El frontend Next.js se comunica con este backend a través de las API routes definidas en `/app/api/`. La URL del backend se configura mediante la variable de entorno `VICKY_API_URL` en el archivo `.env.local` del frontend.

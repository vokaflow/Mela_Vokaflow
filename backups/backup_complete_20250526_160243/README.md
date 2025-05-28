# VokaFlow Frontend (Dashboard)

Este directorio contiene el frontend (dashboard) para el proyecto VokaFlow, diseñado para conectarse con el backend a través de API.

## Configuración

### Base de datos (Neon)

El frontend utiliza Neon Database para almacenar datos específicos del frontend:

```
DATABASE_URL=postgres://neondb_owner:npg_IZ4eEokc3vix@ep-lucky-band-a27phg9c-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

### Conexión al Backend

El frontend se conecta al backend a través de su API en la siguiente URL:

```
BACKEND_API_URL=http://localhost:5000/api
```

## Despliegue con Vercel

Para desplegar el frontend a Vercel:

1. Asegúrate de tener una cuenta en Vercel
2. Configura las variables de entorno en Vercel:
   - `DATABASE_URL`: URL de conexión a Neon DB
   - `BACKEND_API_URL`: URL del backend
   - `NEXT_PUBLIC_STACK_PROJECT_ID`: ID del proyecto Stack
   - `STACK_SECRET_SERVER_KEY`: Clave secreta del servidor Stack

3. Conecta tu repositorio de GitHub a Vercel
4. Configura los ajustes de despliegue

## Desarrollo local

Para desarrollo local:

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

## Integración con Subdominio

Recomendamos configurar subdominios separados para frontend y backend:

- Frontend: `app.tudominio.com` (en Vercel)
- Backend: `api.tudominio.com` (en tu servidor)

## Repositorio Git

El frontend debe mantenerse en el mismo repositorio que el backend, pero en esta carpeta separada, para facilitar el despliegue a Vercel. 
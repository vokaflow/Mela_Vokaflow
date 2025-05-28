import re

# Leer el archivo
with open('src/main.py', 'r') as f:
    content = f.read()

# Comentar la definición del router legacy
content = re.sub(r'^vicky_router = APIRouter.*$', r'# vicky_router = APIRouter(prefix="/vicky", tags=["Vicky"]) # Legacy - comentado', content, flags=re.MULTILINE)

# Encontrar y eliminar todo el bloque de funciones vicky_router
# Patrón para encontrar desde @vicky_router hasta la siguiente función o final
pattern = r'@vicky_router\..*?(?=\n@\w+_router\.|\n@app\.|\nif __name__|\Z)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Comentar el registro del router legacy
content = re.sub(r'^app\.include_router\(vicky_router,.*$', r'# app.include_router(vicky_router, prefix=f"{settings.API_PREFIX}/vicky") # Legacy - comentado', content, flags=re.MULTILINE)

# Agregar importación de nuestro router
if 'from src.backend.routers.vicky import router as vicky_router_new' not in content:
    content = content.replace(
        'from src.backend.routers.health import router as health_router',
        'from src.backend.routers.health import router as health_router\nfrom src.backend.routers.vicky import router as vicky_router_new'
    )

# Agregar registro de nuestro router
if 'vicky_router_new' not in content or 'include_router(vicky_router_new' not in content:
    content = content.replace(
        'app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health")',
        'app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health")\napp.include_router(vicky_router_new, prefix=f"{settings.API_PREFIX}/vicky")'
    )

# Escribir el archivo limpio
with open('src/main.py', 'w') as f:
    f.write(content)

print("✅ Limpieza completada correctamente")

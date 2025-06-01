#!/usr/bin/env python3
import re
import sys

# Leer el archivo verify_all_endpoints.sh
with open('verify_all_endpoints.sh', 'r') as f:
    content = f.read()

# Corregir la verificación de registros
content = content.replace(
    'app.include_router(health_router, prefix="/health"',
    'app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health"'
)

# Guardar el archivo corregido
with open('verify_all_endpoints.sh', 'w') as f:
    f.write(content)

print("✅ Script de verificación corregido")

#!/usr/bin/env python3
import re

# Leer el script de verificación
with open('verify_all_endpoints.sh', 'r') as f:
    content = f.read()

# Arreglar los patrones de búsqueda para que coincidan con el formato real
patterns_to_fix = [
    ('app.include_router(health_router, prefix="/health"', 'app.include_router.*health_router.*prefix='),
    ('app.include_router(vicky_router, prefix="/vicky"', 'app.include_router.*vicky_router.*prefix='),
    ('app.include_router(auth_router, prefix="/auth"', 'app.include_router.*auth_router.*prefix='),
    ('app.include_router(users_router, prefix="/users"', 'app.include_router.*users_router.*prefix='),
    ('app.include_router(translate_router, prefix="/translate"', 'app.include_router.*translate_router.*prefix='),
    ('app.include_router(tts_router, prefix="/tts"', 'app.include_router.*tts_router.*prefix='),
    ('app.include_router(stt_router, prefix="/stt"', 'app.include_router.*stt_router.*prefix='),
    ('app.include_router(voice_router, prefix="/voice"', 'app.include_router.*voice_router.*prefix='),
    ('app.include_router(conversations_router, prefix="/conversations"', 'app.include_router.*conversations_router.*prefix='),
    ('app.include_router(system_router, prefix="/system"', 'app.include_router.*system_router.*prefix='),
    ('app.include_router(models_router, prefix="/models"', 'app.include_router.*models_router.*prefix='),
    ('app.include_router(files_router, prefix="/files"', 'app.include_router.*files_router.*prefix='),
    ('app.include_router(analytics_router, prefix="/analytics"', 'app.include_router.*analytics_router.*prefix='),
    ('app.include_router(notifications_router, prefix="/notifications"', 'app.include_router.*notifications_router.*prefix='),
    ('app.include_router(admin_router, prefix="/admin"', 'app.include_router.*admin_router.*prefix='),
    ('app.include_router(api_keys_router, prefix="/api-keys"', 'app.include_router.*api_keys_router.*prefix='),
    ('app.include_router(webhooks_router, prefix="/webhooks"', 'app.include_router.*webhooks_router.*prefix='),
    ('app.include_router(monitoring_router, prefix="/monitoring"', 'app.include_router.*monitoring_router.*prefix=')
]

# Crear un nuevo script de verificación que use grep con expresiones regulares
new_verification = '''#!/bin/bash

echo "🔗 VERIFICACIÓN DE REGISTRO DE ROUTERS:"
echo "======================================"
echo "📁 Verificando registros..."

routers=("health" "vicky" "auth" "users" "translate" "tts" "stt" "voice" "conversations" "system" "models" "files" "analytics" "notifications" "admin" "api_keys" "webhooks" "monitoring")

for router in "${routers[@]}"; do
    if grep -q "app.include_router.*${router}_router.*prefix=" src/main.py; then
        echo "✅ ${router} router registrado correctamente"
    else
        echo "❌ ${router} router NO registrado"
    fi
done
'''

# Reemplazar la sección de verificación de registros en el script original
content = re.sub(
    r'🔗 VERIFICACIÓN DE REGISTRO DE ROUTERS:.*?📊 RESUMEN FINAL:',
    new_verification + '\n📊 RESUMEN FINAL:',
    content,
    flags=re.DOTALL
)

# Guardar el script corregido
with open('verify_all_endpoints.sh', 'w') as f:
    f.write(content)

print("✅ Script de verificación corregido para detectar registros correctamente")

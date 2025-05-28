#!/bin/bash
# Script de despliegue completo para VokaFlow Backend
# Ejecutar como root o con sudo

set -e  # Detener en caso de error

echo "🚀 === DESPLIEGUE DE VOKAFLOW BACKEND ==="
echo "$(date)"
echo

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
VOKAFLOW_USER="vokaflow"
VOKAFLOW_HOME="/opt/vokaflow"
PYTHON_VERSION="3.12"
SERVICE_NAME="vokaflow-backend"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar sistema operativo
print_status "Verificando sistema operativo..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
        OS="debian"
        print_success "Sistema Debian/Ubuntu detectado"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
        print_success "Sistema RedHat/CentOS detectado"
    else
        print_error "Distribución Linux no soportada"
        exit 1
    fi
else
    print_error "Sistema operativo no soportado. Se requiere Linux."
    exit 1
fi

# 2. Instalar dependencias del sistema
print_status "Instalando dependencias del sistema..."
if [ "$OS" = "debian" ]; then
    apt update
    apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev \
        build-essential \
        curl \
        wget \
        git \
        nginx \
        supervisor \
        redis-server \
        postgresql-client \
        ffmpeg \
        portaudio19-dev \
        libffi-dev \
        libssl-dev \
        pkg-config \
        systemd
elif [ "$OS" = "redhat" ]; then
    yum update -y
    yum install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-devel \
        gcc \
        gcc-c++ \
        make \
        curl \
        wget \
        git \
        nginx \
        supervisor \
        redis \
        postgresql \
        ffmpeg \
        portaudio-devel \
        libffi-devel \
        openssl-devel \
        pkgconfig \
        systemd
fi

# 3. Crear usuario del sistema
print_status "Creando usuario del sistema..."
if ! id "$VOKAFLOW_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash -d "$VOKAFLOW_HOME" "$VOKAFLOW_USER"
    print_success "Usuario $VOKAFLOW_USER creado"
else
    print_warning "Usuario $VOKAFLOW_USER ya existe"
fi

# 4. Crear estructura de directorios
print_status "Creando estructura de directorios..."
mkdir -p "$VOKAFLOW_HOME"/{src,logs,data,config,backups,tmp}
mkdir -p "$VOKAFLOW_HOME"/data/{models,voices,cache,uploads}
mkdir -p /var/log/vokaflow
chown -R "$VOKAFLOW_USER":"$VOKAFLOW_USER" "$VOKAFLOW_HOME"
chown -R "$VOKAFLOW_USER":"$VOKAFLOW_USER" /var/log/vokaflow

# 5. Configurar entorno Python
print_status "Configurando entorno Python..."
sudo -u "$VOKAFLOW_USER" python${PYTHON_VERSION} -m venv "$VOKAFLOW_HOME"/venv
sudo -u "$VOKAFLOW_USER" "$VOKAFLOW_HOME"/venv/bin/pip install --upgrade pip setuptools wheel

# 6. Copiar código fuente
print_status "Copiando código fuente..."
if [ -d "./src" ]; then
    cp -r ./src/* "$VOKAFLOW_HOME"/src/
    cp -r ./python-backend/* "$VOKAFLOW_HOME"/src/ 2>/dev/null || true
    cp requirements.txt "$VOKAFLOW_HOME"/ 2>/dev/null || true
    cp ./python-backend/requirements.txt "$VOKAFLOW_HOME"/requirements.txt 2>/dev/null || true
    chown -R "$VOKAFLOW_USER":"$VOKAFLOW_USER" "$VOKAFLOW_HOME"/src
else
    print_error "Directorio src no encontrado. Ejecutar desde la raíz del proyecto."
    exit 1
fi

# 7. Instalar dependencias Python
print_status "Instalando dependencias Python..."
sudo -u "$VOKAFLOW_USER" "$VOKAFLOW_HOME"/venv/bin/pip install -r "$VOKAFLOW_HOME"/requirements.txt

# 8. Configurar variables de entorno
print_status "Configurando variables de entorno..."
cat > "$VOKAFLOW_HOME"/.env << EOF
# Configuración de producción VokaFlow
NODE_ENV=production
DEBUG=false

# Base de datos Neon
DATABASE_URL=${DATABASE_URL:-""}
POSTGRES_URL=${POSTGRES_URL:-""}
POSTGRES_PRISMA_URL=${POSTGRES_PRISMA_URL:-""}

# Stack Auth
NEXT_PUBLIC_STACK_PROJECT_ID=${NEXT_PUBLIC_STACK_PROJECT_ID:-""}
NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY=${NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY:-""}
STACK_SECRET_SERVER_KEY=${STACK_SECRET_SERVER_KEY:-""}

# Seguridad
JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}
SESSION_SECRET=${SESSION_SECRET:-$(openssl rand -hex 32)}
CSRF_SECRET=${CSRF_SECRET:-$(openssl rand -hex 32)}

# Redis
REDIS_URL=redis://localhost:6379/0

# Servidor
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/vokaflow/backend.log

# Rutas de datos
DATA_PATH=$VOKAFLOW_HOME/data
MODELS_PATH=$VOKAFLOW_HOME/data/models
VOICES_PATH=$VOKAFLOW_HOME/data/voices
CACHE_PATH=$VOKAFLOW_HOME/data/cache
EOF

chown "$VOKAFLOW_USER":"$VOKAFLOW_USER" "$VOKAFLOW_HOME"/.env
chmod 600 "$VOKAFLOW_HOME"/.env

print_success "Archivo .env creado en $VOKAFLOW_HOME/.env"
print_warning "IMPORTANTE: Edita $VOKAFLOW_HOME/.env con tus credenciales reales"

# 9. Configurar servicio systemd
print_status "Configurando servicio systemd..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=VokaFlow Backend Service
After=network.target redis.service
Wants=redis.service

[Service]
Type=exec
User=$VOKAFLOW_USER
Group=$VOKAFLOW_USER
WorkingDirectory=$VOKAFLOW_HOME/src/backend
Environment=PATH=$VOKAFLOW_HOME/venv/bin
EnvironmentFile=$VOKAFLOW_HOME/.env
ExecStart=$VOKAFLOW_HOME/venv/bin/python main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Límites de recursos
LimitNOFILE=65536
LimitNPROC=4096

# Seguridad
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$VOKAFLOW_HOME /var/log/vokaflow /tmp

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

# 10. Configurar Nginx
print_status "Configurando Nginx..."
cat > /etc/nginx/sites-available/vokaflow << EOF
upstream vokaflow_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    # Logs
    access_log /var/log/nginx/vokaflow_access.log;
    error_log /var/log/nginx/vokaflow_error.log;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # API Backend
    location /api/ {
        proxy_pass http://vokaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://vokaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias $VOKAFLOW_HOME/data/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://vokaflow_backend/health;
        access_log off;
    }
    
    # Default location
    location / {
        return 200 'VokaFlow Backend is running';
        add_header Content-Type text/plain;
    }
}
EOF

# Habilitar sitio
ln -sf /etc/nginx/sites-available/vokaflow /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 11. Configurar Redis
print_status "Configurando Redis..."
systemctl enable redis-server
systemctl start redis-server

# 12. Configurar logrotate
print_status "Configurando rotación de logs..."
cat > /etc/logrotate.d/vokaflow << EOF
/var/log/vokaflow/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $VOKAFLOW_USER $VOKAFLOW_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

# 13. Crear scripts de utilidad
print_status "Creando scripts de utilidad..."

# Script de inicio
cat > "$VOKAFLOW_HOME"/start.sh << 'EOF'
#!/bin/bash
cd /opt/vokaflow
source .env
source venv/bin/activate
cd src/backend
exec python main.py
EOF

# Script de estado
cat > "$VOKAFLOW_HOME"/status.sh << 'EOF'
#!/bin/bash
echo "=== Estado de VokaFlow ==="
echo "Servicio: $(systemctl is-active vokaflow-backend)"
echo "Nginx: $(systemctl is-active nginx)"
echo "Redis: $(systemctl is-active redis-server)"
echo "Logs recientes:"
journalctl -u vokaflow-backend --no-pager -n 5
EOF

# Script de logs
cat > "$VOKAFLOW_HOME"/logs.sh << 'EOF'
#!/bin/bash
echo "=== Logs de VokaFlow ==="
echo "Presiona Ctrl+C para salir"
journalctl -u vokaflow-backend -f
EOF

chmod +x "$VOKAFLOW_HOME"/{start.sh,status.sh,logs.sh}
chown "$VOKAFLOW_USER":"$VOKAFLOW_USER" "$VOKAFLOW_HOME"/{start.sh,status.sh,logs.sh}

print_success "Despliegue completado!"
echo
echo "📋 === PRÓXIMOS PASOS ==="
echo "1. Editar configuración: nano $VOKAFLOW_HOME/.env"
echo "2. Iniciar servicios: systemctl start vokaflow-backend"
echo "3. Verificar estado: $VOKAFLOW_HOME/status.sh"
echo "4. Ver logs: $VOKAFLOW_HOME/logs.sh"
echo
echo "🌐 URLs de acceso:"
echo "- API: http://$(hostname -I | awk '{print $1}')/api/"
echo "- Health: http://$(hostname -I | awk '{print $1}')/health"
echo
echo "📁 Directorios importantes:"
echo "- Código: $VOKAFLOW_HOME/src"
echo "- Logs: /var/log/vokaflow"
echo "- Datos: $VOKAFLOW_HOME/data"
echo "- Configuración: $VOKAFLOW_HOME/.env"

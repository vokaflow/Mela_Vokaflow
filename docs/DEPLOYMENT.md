# 🚀 Guía de Deployment VokaFlow

Esta guía detalla todos los métodos de deployment para VokaFlow, desde desarrollo local hasta producción enterprise.

## 📋 Contenido

- [🏠 Desarrollo Local](#-desarrollo-local)
- [🧪 Staging Environment](#-staging-environment)  
- [🏭 Producción Enterprise](#-producción-enterprise)
- [🐳 Docker Deployment](#-docker-deployment)
- [☸️ Kubernetes Deployment](#️-kubernetes-deployment)
- [☁️ Cloud Providers](#️-cloud-providers)
- [🔧 Configuración Avanzada](#-configuración-avanzada)

## 🏠 Desarrollo Local

### Requisitos Mínimos

```bash
# Sistema Operativo
Ubuntu 20.04+ / CentOS 8+ / macOS 11+

# Software
Python 3.12+
Redis 7.0+
Git 2.30+

# Hardware
CPU: 2+ cores
RAM: 4GB+
Disk: 10GB+ disponible
```

### Setup Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-org/vokaflow.git
cd vokaflow

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar Redis local
sudo apt update
sudo apt install redis-server

# 5. Iniciar en modo desarrollo
export VOKAFLOW_ENV=development
python src/main.py
```

### Configuración de Desarrollo

```bash
# variables de entorno desarrollo
export VOKAFLOW_ENV=development
export VOKAFLOW_REDIS_CLUSTER=false
export VOKAFLOW_HIGH_SCALE=false
export VOKAFLOW_LOG_LEVEL=DEBUG
export REDIS_URL=redis://localhost:6379
```

## 🧪 Staging Environment

### Arquitectura de Staging

```yaml
# staging-compose.yml
version: '3.8'
services:
  vokaflow-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VOKAFLOW_ENV=staging
      - VOKAFLOW_REDIS_CLUSTER=true
      - VOKAFLOW_HIGH_SCALE=true
    depends_on:
      - redis-cluster
      - monitoring

  redis-cluster:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes
    ports:
      - "7000-7005:7000-7005"
    volumes:
      - redis-data:/data

  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  redis-data:
  grafana-data:
```

### Setup de Staging

```bash
# 1. Preparar servidor staging
ssh user@staging-server.com

# 2. Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Clonar y configurar
git clone https://github.com/tu-org/vokaflow.git
cd vokaflow

# 4. Configurar variables de entorno
cp .env.staging.example .env.staging
# Editar .env.staging con configuraciones específicas

# 5. Desplegar
docker-compose -f staging-compose.yml up -d

# 6. Verificar deployment
curl http://staging-server.com:8000/api/health/
```

## 🏭 Producción Enterprise

### Arquitectura de Producción

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                   │
│                     (SSL Termination)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────────────┐
│                VokaFlow Cluster                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ VokaFlow 1  │  │ VokaFlow 2  │  │ VokaFlow 3  │         │
│  │ (Primary)   │  │ (Secondary) │  │ (Secondary) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────────────┐
│                Redis Cluster                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │Master 1 │ │Master 2 │ │Master 3 │ │ Slave 1 │ │Slave 2 │ │
│  │(Primary)│ │(Primary)│ │(Primary)│ │(Backup) │ │(Backup)│ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Automático de Producción

```bash
# Usar el script de deployment automatizado
python deploy_production_cluster.py

# O seguir pasos manuales:

# 1. Preparar servidores de producción
# Server 1: Load Balancer + Monitoring
# Server 2-4: VokaFlow Application Nodes  
# Server 5-10: Redis Cluster Nodes

# 2. Configurar Load Balancer (Nginx)
sudo apt install nginx
# Copiar configuración nginx
sudo cp configs/nginx/vokaflow-production.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/vokaflow-production.conf /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# 3. Setup Redis Cluster en múltiples servidores
python setup_multi_server_redis.py

# 4. Desplegar VokaFlow en múltiples nodos
ansible-playbook -i inventory/production.yml playbooks/deploy-vokaflow.yml

# 5. Configurar monitoreo
python setup_production_monitoring.py
```

### Configuración de Nginx

```nginx
# /etc/nginx/sites-available/vokaflow-production.conf
upstream vokaflow_backend {
    least_conn;
    server 10.0.1.10:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 weight=2 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=2 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.vokaflow.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.vokaflow.com;

    ssl_certificate /etc/ssl/certs/vokaflow.crt;
    ssl_certificate_key /etc/ssl/private/vokaflow.key;
    
    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=1000r/s;
    limit_req zone=api_limit burst=2000 nodelay;

    location / {
        proxy_pass http://vokaflow_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Health checks
        proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
    }

    # Health check endpoint (bypass load balancing)
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/api/health/;
    }

    # Metrics endpoint (internal only)
    location /metrics {
        allow 10.0.0.0/8;
        deny all;
        proxy_pass http://vokaflow_backend/api/high-scale-tasks/metrics;
    }
}
```

## 🐳 Docker Deployment

### Dockerfile Optimizado

```dockerfile
# Dockerfile.production
FROM python:3.12-slim-bullseye as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r vokaflow && useradd -r -g vokaflow vokaflow

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/

# Set permissions
RUN chown -R vokaflow:vokaflow /app
USER vokaflow

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

EXPOSE 8000

# Production command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose para Producción

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  vokaflow-api:
    build:
      context: .
      dockerfile: Dockerfile.production
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    environment:
      - VOKAFLOW_ENV=production
      - VOKAFLOW_REDIS_CLUSTER=true
      - VOKAFLOW_HIGH_SCALE=true
    networks:
      - vokaflow-network
    depends_on:
      - redis-cluster

  redis-master-1:
    image: redis:7-alpine
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - ./configs/redis/redis-7000.conf:/usr/local/etc/redis/redis.conf
      - redis-data-1:/data
    ports:
      - "7000:7000"
    networks:
      - vokaflow-network

  redis-master-2:
    image: redis:7-alpine
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - ./configs/redis/redis-7001.conf:/usr/local/etc/redis/redis.conf
      - redis-data-2:/data
    ports:
      - "7001:7001"
    networks:
      - vokaflow-network

  redis-master-3:
    image: redis:7-alpine
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - ./configs/redis/redis-7002.conf:/usr/local/etc/redis/redis.conf
      - redis-data-3:/data
    ports:
      - "7002:7002"
    networks:
      - vokaflow-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./configs/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    networks:
      - vokaflow-network
    depends_on:
      - vokaflow-api

  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password_here
    volumes:
      - grafana-data:/var/lib/grafana
      - ./configs/grafana:/etc/grafana/provisioning
    networks:
      - vokaflow-network

volumes:
  redis-data-1:
  redis-data-2:
  redis-data-3:
  grafana-data:

networks:
  vokaflow-network:
    driver: bridge
```

### Comandos Docker

```bash
# Build production image
docker build -f Dockerfile.production -t vokaflow:latest .

# Run production stack
docker-compose -f docker-compose.production.yml up -d

# Scale API instances
docker-compose -f docker-compose.production.yml up -d --scale vokaflow-api=5

# View logs
docker-compose -f docker-compose.production.yml logs -f vokaflow-api

# Update deployment
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

## ☸️ Kubernetes Deployment

### Namespace y Configuración Base

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vokaflow-production
  labels:
    name: vokaflow-production
    environment: production
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vokaflow-config
  namespace: vokaflow-production
data:
  VOKAFLOW_ENV: "production"
  VOKAFLOW_REDIS_CLUSTER: "true"
  VOKAFLOW_HIGH_SCALE: "true"
  VOKAFLOW_LOG_LEVEL: "INFO"
  REDIS_CLUSTER_NODES: "redis-0.redis-headless:7000,redis-1.redis-headless:7000,redis-2.redis-headless:7000"
```

### Redis Cluster StatefulSet

```yaml
# k8s/redis-cluster.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: vokaflow-production
spec:
  serviceName: redis-headless
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
          - redis-server
          - /etc/redis/redis.conf
          - --cluster-enabled
          - "yes"
          - --cluster-config-file
          - nodes.conf
          - --cluster-node-timeout
          - "15000"
        ports:
        - containerPort: 6379
          name: client
        - containerPort: 16379
          name: gossip
        volumeMounts:
        - name: redis-data
          mountPath: /data
        - name: redis-config
          mountPath: /etc/redis
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### VokaFlow Deployment

```yaml
# k8s/vokaflow-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vokaflow-api
  namespace: vokaflow-production
  labels:
    app: vokaflow-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2
  selector:
    matchLabels:
      app: vokaflow-api
  template:
    metadata:
      labels:
        app: vokaflow-api
    spec:
      containers:
      - name: vokaflow-api
        image: vokaflow:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: vokaflow-config
        livenessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: vokaflow-service
  namespace: vokaflow-production
spec:
  selector:
    app: vokaflow-api
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vokaflow-ingress
  namespace: vokaflow-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-burst: "2000"
spec:
  tls:
  - hosts:
    - api.vokaflow.com
    secretName: vokaflow-tls
  rules:
  - host: api.vokaflow.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vokaflow-service
            port:
              number: 80
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vokaflow-hpa
  namespace: vokaflow-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vokaflow-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
```

### Comandos Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n vokaflow-production
kubectl get services -n vokaflow-production

# View logs
kubectl logs -f deployment/vokaflow-api -n vokaflow-production

# Scale manually
kubectl scale deployment vokaflow-api --replicas=5 -n vokaflow-production

# Rolling update
kubectl set image deployment/vokaflow-api vokaflow-api=vokaflow:v2.0.0 -n vokaflow-production

# Port forwarding for testing
kubectl port-forward service/vokaflow-service 8000:80 -n vokaflow-production
```

## ☁️ Cloud Providers

### AWS Deployment

```yaml
# aws/cloudformation-template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VokaFlow Production Infrastructure'

Parameters:
  EnvironmentName:
    Description: Environment name prefix
    Type: String
    Default: vokaflow-prod

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-VPC

  # EKS Cluster
  EKSCluster:
    Type: AWS::EKS::Cluster
    Properties:
      Name: !Sub ${EnvironmentName}-cluster
      Version: '1.24'
      RoleArn: !GetAtt EKSServiceRole.Arn
      ResourcesVpcConfig:
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
          - !Ref PublicSubnet1
          - !Ref PublicSubnet2

  # ElastiCache Redis Cluster
  RedisSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Redis cluster
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  RedisCluster:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: VokaFlow Redis Cluster
      NumCacheClusters: 6
      Engine: redis
      CacheNodeType: cache.r6g.large
      Port: 6379
      CacheSubnetGroupName: !Ref RedisSubnetGroup
      SecurityGroupIds:
        - !Ref RedisSecurityGroup

  # Application Load Balancer
  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${EnvironmentName}-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

Outputs:
  ClusterName:
    Description: EKS cluster name
    Value: !Ref EKSCluster
    Export:
      Name: !Sub ${EnvironmentName}-ClusterName

  RedisEndpoint:
    Description: Redis cluster endpoint
    Value: !GetAtt RedisCluster.PrimaryEndPoint.Address
    Export:
      Name: !Sub ${EnvironmentName}-RedisEndpoint
```

### Google Cloud Platform

```yaml
# gcp/deployment-manager-template.yaml
resources:
- name: vokaflow-gke-cluster
  type: container.v1.cluster
  properties:
    zone: us-central1-a
    cluster:
      name: vokaflow-production
      initialNodeCount: 3
      nodeConfig:
        machineType: n1-standard-4
        diskSizeGb: 100
        oauthScopes:
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/devstorage.read_only
        - https://www.googleapis.com/auth/logging.write
        - https://www.googleapis.com/auth/monitoring

- name: vokaflow-redis
  type: redis.v1.instance
  properties:
    instanceId: vokaflow-redis-cluster
    tier: STANDARD_HA
    memorySizeGb: 5
    region: us-central1
    redisVersion: REDIS_7_0
```

### Azure Deployment

```yaml
# azure/arm-template.json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "clusterName": {
      "type": "string",
      "defaultValue": "vokaflow-aks",
      "metadata": {
        "description": "The name of the Managed Cluster resource."
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.ContainerService/managedClusters",
      "apiVersion": "2021-03-01",
      "name": "[parameters('clusterName')]",
      "location": "[resourceGroup().location]",
      "properties": {
        "dnsPrefix": "[parameters('clusterName')]",
        "agentPoolProfiles": [
          {
            "name": "agentpool",
            "count": 3,
            "vmSize": "Standard_D4s_v3",
            "osType": "Linux",
            "mode": "System"
          }
        ]
      }
    }
  ]
}
```

## 🔧 Configuración Avanzada

### SSL/TLS Configuration

```bash
# Generar certificados con Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.vokaflow.com

# O usar certificados personalizados
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
    -keyout /etc/ssl/private/vokaflow.key \
    -out /etc/ssl/certs/vokaflow.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=api.vokaflow.com"
```

### Backup y Recovery

```bash
# Backup de Redis Cluster
#!/bin/bash
# backup-redis.sh
BACKUP_DIR="/backup/redis/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

for port in {7000..7005}; do
    redis-cli -p $port --rdb $BACKUP_DIR/dump-$port.rdb
done

# Comprimir backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Enviar a S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vokaflow-backups/redis/
```

### Monitoring Stack

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "vokaflow_rules.yml"

scrape_configs:
  - job_name: 'vokaflow-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/high-scale-tasks/metrics'
    scrape_interval: 10s

  - job_name: 'redis-cluster'
    static_configs:
      - targets: 
        - 'localhost:7000'
        - 'localhost:7001'
        - 'localhost:7002'
        - 'localhost:7003'
        - 'localhost:7004'
        - 'localhost:7005'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Disaster Recovery Plan

```bash
# disaster-recovery.sh
#!/bin/bash

# 1. Verificar estado del cluster
check_cluster_health() {
    redis-cli --cluster check 127.0.0.1:7000
}

# 2. Restaurar desde backup
restore_from_backup() {
    BACKUP_FILE=$1
    tar -xzf $BACKUP_FILE
    
    for port in {7000..7005}; do
        redis-cli -p $port FLUSHALL
        redis-cli -p $port --pipe < dump-$port.rdb
    done
}

# 3. Recrear cluster si es necesario
recreate_cluster() {
    redis-cli --cluster create \
        127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
        127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
        --cluster-replicas 1 --cluster-yes
}

# Ejecutar plan de recuperación
if ! check_cluster_health; then
    echo "Cluster unhealthy, initiating recovery..."
    restore_from_backup $1
    recreate_cluster
    echo "Recovery completed"
fi
```

### Performance Tuning

```bash
# system-optimization.sh
#!/bin/bash

# Optimizaciones del kernel para alta carga
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
echo 'fs.file-max = 1000000' >> /etc/sysctl.conf

# Límites de archivos
echo '* soft nofile 1000000' >> /etc/security/limits.conf
echo '* hard nofile 1000000' >> /etc/security/limits.conf

# Aplicar cambios
sysctl -p
```

## ✅ Validación Post-Deployment

```bash
# validation-suite.sh
#!/bin/bash

# 1. Health checks
echo "Testing health endpoints..."
curl -f http://localhost:8000/api/health/ || exit 1

# 2. Performance tests
echo "Running performance tests..."
python production_system_demo.py

# 3. Load testing
echo "Running load tests..."
ab -n 10000 -c 100 http://localhost:8000/api/health/

# 4. Redis cluster validation
echo "Validating Redis cluster..."
redis-cli --cluster check 127.0.0.1:7000

# 5. Monitoring validation
echo "Checking monitoring..."
curl -f http://localhost:8000/api/high-scale-tasks/metrics | jq .

echo "All validations passed! 🎉"
```

Esta documentación proporciona una guía completa para deployar VokaFlow en cualquier entorno, desde desarrollo local hasta producción enterprise con alta disponibilidad. 
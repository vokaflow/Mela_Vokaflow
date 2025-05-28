from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import time
from datetime import datetime
import subprocess
import shutil

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime: float

class SystemStatus(BaseModel):
    cpu_cores: str
    memory_usage: str
    disk_usage: str
    load_average: str
    status: str

class VersionInfo(BaseModel):
    version: str
    build: str
    environment: str
    last_updated: str
    python_version: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check básico del sistema"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        uptime=time.time()
    )

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Estado del sistema usando comandos nativos de Linux"""
    try:
        # CPU cores
        cpu_cores = subprocess.getoutput("nproc").strip() + " cores"
        
        # Memory usage
        memory_usage = subprocess.getoutput("free -h | grep '^Mem:' | awk '{print $3\"/\"$2\" (\"$3/$2*100\"%)\"}'").strip()
        
        # Disk usage
        disk_usage = subprocess.getoutput("df -h / | tail -1 | awk '{print $5\" used of \"$2}'").strip()
        
        # Load average
        load_average = subprocess.getoutput("uptime | awk -F'load average:' '{print $2}'").strip()
        
        return SystemStatus(
            cpu_cores=cpu_cores,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            load_average=load_average,
            status="healthy"
        )
    except Exception as e:
        return SystemStatus(
            cpu_cores="Error",
            memory_usage="Error",
            disk_usage="Error", 
            load_average="Error",
            status="error"
        )

@router.get("/version", response_model=VersionInfo)
async def get_version():
    """Información de versión del sistema"""
    python_version = subprocess.getoutput("python3 --version").strip()
    
    return VersionInfo(
        version="1.0.0",
        build="2024.01.001",
        environment="production",
        last_updated=datetime.now().isoformat(),
        python_version=python_version
    )

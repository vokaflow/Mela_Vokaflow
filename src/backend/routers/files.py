"""
Router para Files & Media - Gestión completa de archivos y medios
"""
import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, BinaryIO
from enum import Enum
import logging
import asyncio
import aiofiles
from PIL import Image
import ffmpeg

from fastapi import (
    APIRouter, HTTPException, Depends, status, UploadFile, File, 
    Form, Query, BackgroundTasks, Response
)
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, LargeBinary

# Importaciones locales
from ..database import get_db, Base
from ..auth import get_current_user, get_current_active_user
from ..models import UserDB

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuración
UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp")
THUMBNAILS_DIR = Path("thumbnails")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
    'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'],
    'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
    'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
    'archive': ['.zip', '.rar', '.7z', '.tar', '.gz']
}

# Crear directorios necesarios
for directory in [UPLOAD_DIR, TEMP_DIR, THUMBNAILS_DIR]:
    directory.mkdir(exist_ok=True)

# Modelos de base de datos
class FileDB(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    file_type = Column(String(50))  # image, audio, video, document, archive
    file_hash = Column(String(64))  # SHA-256
    thumbnail_path = Column(String(500), nullable=True)
    file_meta = Column(Text, nullable=True)  # JSON metadata
    is_public = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

# Modelos Pydantic
class FileType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"

class FileInfo(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    file_type: FileType
    file_hash: str
    thumbnail_url: Optional[str] = None
    file_metadata: Optional[Dict[str, Any]] = None
    is_public: bool
    download_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    download_url: str
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    success: bool
    file_id: int
    filename: str
    file_size: int
    file_type: FileType
    download_url: str
    thumbnail_url: Optional[str] = None
    processing_status: str = "completed"

class FileStats(BaseModel):
    total_files: int
    total_size: int
    files_by_type: Dict[str, int]
    recent_uploads: List[FileInfo]
    most_downloaded: List[FileInfo]
    storage_usage: Dict[str, Any]

class BulkUploadResponse(BaseModel):
    success: bool
    uploaded_files: List[FileUploadResponse]
    failed_files: List[Dict[str, str]]
    total_uploaded: int
    total_failed: int

class FileProcessingJob(BaseModel):
    job_id: str
    file_id: int
    status: str  # pending, processing, completed, failed
    progress: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

# Utilidades para archivos
class FileManager:
    @staticmethod
    def get_file_type(filename: str) -> FileType:
        """Determina el tipo de archivo basado en la extensión"""
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return FileType(file_type)
        
        return FileType.OTHER
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Calcula el hash SHA-256 del archivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @staticmethod
    async def create_thumbnail(file_path: Path, file_type: FileType) -> Optional[Path]:
        """Crea una miniatura del archivo si es posible"""
        try:
            thumbnail_path = THUMBNAILS_DIR / f"{file_path.stem}_thumb.jpg"
            
            if file_type == FileType.IMAGE:
                # Crear miniatura de imagen
                with Image.open(file_path) as img:
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    img.convert('RGB').save(thumbnail_path, 'JPEG', quality=85)
                return thumbnail_path
                
            elif file_type == FileType.VIDEO:
                # Crear miniatura de video usando ffmpeg
                try:
                    (
                        ffmpeg
                        .input(str(file_path), ss=1)
                        .output(str(thumbnail_path), vframes=1, format='image2', vcodec='mjpeg')
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                    return thumbnail_path
                except Exception as e:
                    logger.warning(f"No se pudo crear miniatura de video: {e}")
                    
            return None
            
        except Exception as e:
            logger.error(f"Error al crear miniatura: {e}")
            return None
    
    @staticmethod
    def get_file_metadata(file_path: Path, file_type: FileType) -> Dict[str, Any]:
        """Extrae metadata del archivo"""
        metadata = {}
        
        try:
            if file_type == FileType.IMAGE:
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode
                    })
                    
            elif file_type == FileType.AUDIO:
                try:
                    probe = ffmpeg.probe(str(file_path))
                    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
                    if audio_stream:
                        metadata.update({
                            "duration": float(audio_stream.get('duration', 0)),
                            "bit_rate": int(audio_stream.get('bit_rate', 0)),
                            "sample_rate": int(audio_stream.get('sample_rate', 0)),
                            "channels": int(audio_stream.get('channels', 0))
                        })
                except Exception as e:
                    logger.warning(f"No se pudo extraer metadata de audio: {e}")
                    
            elif file_type == FileType.VIDEO:
                try:
                    probe = ffmpeg.probe(str(file_path))
                    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                    if video_stream:
                        metadata.update({
                            "duration": float(video_stream.get('duration', 0)),
                            "width": int(video_stream.get('width', 0)),
                            "height": int(video_stream.get('height', 0)),
                            "fps": eval(video_stream.get('r_frame_rate', '0/1')),
                            "bit_rate": int(video_stream.get('bit_rate', 0))
                        })
                except Exception as e:
                    logger.warning(f"No se pudo extraer metadata de video: {e}")
                    
        except Exception as e:
            logger.error(f"Error al extraer metadata: {e}")
            
        return metadata

file_manager = FileManager()

# Endpoints

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    is_public: bool = Form(False),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo al servidor
    """
    try:
        # Validar tamaño del archivo
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo es demasiado grande. Máximo permitido: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Determinar tipo de archivo
        file_type = file_manager.get_file_type(file.filename)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Calcular hash y metadata
        file_hash = file_manager.calculate_file_hash(file_path)
        file_size = file_path.stat().st_size
        mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        
        # Verificar si el archivo ya existe (por hash)
        existing_file = db.query(FileDB).filter(
            FileDB.file_hash == file_hash,
            FileDB.user_id == current_user.id
        ).first()
        
        if existing_file:
            # Eliminar archivo duplicado
            file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este archivo ya existe en tu biblioteca"
            )
        
        # Crear registro en base de datos
        db_file = FileDB(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=mime_type,
            file_type=file_type.value,
            file_hash=file_hash,
            is_public=is_public
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Procesar archivo en segundo plano
        background_tasks.add_task(
            process_file_background,
            db_file.id,
            file_path,
            file_type
        )
        
        return FileUploadResponse(
            success=True,
            file_id=db_file.id,
            filename=unique_filename,
            file_size=file_size,
            file_type=file_type,
            download_url=f"/api/files/{db_file.id}/download",
            processing_status="processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al subir archivo: {e}")
        # Limpiar archivo si existe
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al subir el archivo"
        )

@router.post("/upload/bulk", response_model=BulkUploadResponse)
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    is_public: bool = Form(False),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sube múltiples archivos al servidor
    """
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # Reutilizar lógica de upload individual
            result = await upload_file(
                background_tasks=background_tasks,
                file=file,
                is_public=is_public,
                current_user=current_user,
                db=db
            )
            uploaded_files.append(result)
            
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return BulkUploadResponse(
        success=len(uploaded_files) > 0,
        uploaded_files=uploaded_files,
        failed_files=failed_files,
        total_uploaded=len(uploaded_files),
        total_failed=len(failed_files)
    )

@router.get("/", response_model=List[FileInfo])
async def list_files(
    file_type: Optional[FileType] = None,
    is_public: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista los archivos del usuario
    """
    try:
        query = db.query(FileDB).filter(FileDB.user_id == current_user.id)
        
        if file_type:
            query = query.filter(FileDB.file_type == file_type.value)
        
        if is_public is not None:
            query = query.filter(FileDB.is_public == is_public)
        
        files = query.order_by(FileDB.created_at.desc()).offset(skip).limit(limit).all()
        
        # Convertir a FileInfo con URLs
        file_infos = []
        for file in files:
            file_info = FileInfo.from_orm(file)
            file_info.download_url = f"/api/files/{file.id}/download"
            if file.thumbnail_path:
                file_info.thumbnail_url = f"/api/files/{file.id}/thumbnail"
            file_infos.append(file_info)
        
        return file_infos
        
    except Exception as e:
        logger.error(f"Error al listar archivos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de archivos"
        )

@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene información detallada de un archivo
    """
    file = db.query(FileDB).filter(
        FileDB.id == file_id,
        FileDB.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    file_info = FileInfo.from_orm(file)
    file_info.download_url = f"/api/files/{file.id}/download"
    if file.thumbnail_path:
        file_info.thumbnail_url = f"/api/files/{file.id}/thumbnail"
    
    return file_info

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: Optional[UserDB] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Descarga un archivo
    """
    # Buscar archivo
    query = db.query(FileDB).filter(FileDB.id == file_id)
    
    # Si no hay usuario autenticado, solo archivos públicos
    if not current_user:
        query = query.filter(FileDB.is_public == True)
    else:
        # Usuario autenticado puede ver sus archivos o archivos públicos
        query = query.filter(
            (FileDB.user_id == current_user.id) | (FileDB.is_public == True)
        )
    
    file = query.first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo físico no encontrado"
        )
    
    # Incrementar contador de descargas
    file.download_count += 1
    db.commit()
    
    return FileResponse(
        path=file_path,
        filename=file.original_filename,
        media_type=file.mime_type
    )

@router.get("/{file_id}/thumbnail")
async def get_thumbnail(
    file_id: int,
    current_user: Optional[UserDB] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene la miniatura de un archivo
    """
    # Buscar archivo (misma lógica que download)
    query = db.query(FileDB).filter(FileDB.id == file_id)
    
    if not current_user:
        query = query.filter(FileDB.is_public == True)
    else:
        query = query.filter(
            (FileDB.user_id == current_user.id) | (FileDB.is_public == True)
        )
    
    file = query.first()
    
    if not file or not file.thumbnail_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miniatura no encontrada"
        )
    
    thumbnail_path = Path(file.thumbnail_path)
    if not thumbnail_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de miniatura no encontrado"
        )
    
    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg"
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un archivo
    """
    file = db.query(FileDB).filter(
        FileDB.id == file_id,
        FileDB.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    try:
        # Eliminar archivo físico
        file_path = Path(file.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Eliminar miniatura si existe
        if file.thumbnail_path:
            thumbnail_path = Path(file.thumbnail_path)
            if thumbnail_path.exists():
                thumbnail_path.unlink()
        
        # Eliminar registro de base de datos
        db.delete(file)
        db.commit()
        
        return {"success": True, "message": "Archivo eliminado correctamente"}
        
    except Exception as e:
        logger.error(f"Error al eliminar archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el archivo"
        )

@router.put("/{file_id}")
async def update_file(
    file_id: int,
    is_public: Optional[bool] = None,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza propiedades de un archivo
    """
    file = db.query(FileDB).filter(
        FileDB.id == file_id,
        FileDB.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    # Actualizar propiedades
    if is_public is not None:
        file.is_public = is_public
    
    file.updated_at = datetime.now()
    db.commit()
    db.refresh(file)
    
    file_info = FileInfo.from_orm(file)
    file_info.download_url = f"/api/files/{file.id}/download"
    if file.thumbnail_path:
        file_info.thumbnail_url = f"/api/files/{file.id}/thumbnail"
    
    return file_info

@router.get("/stats/overview", response_model=FileStats)
async def get_file_stats(
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de archivos del usuario
    """
    try:
        # Estadísticas básicas
        total_files = db.query(FileDB).filter(FileDB.user_id == current_user.id).count()
        
        # Tamaño total
        total_size_result = db.query(db.func.sum(FileDB.file_size)).filter(
            FileDB.user_id == current_user.id
        ).scalar() or 0
        
        # Archivos por tipo
        files_by_type = {}
        for file_type in FileType:
            count = db.query(FileDB).filter(
                FileDB.user_id == current_user.id,
                FileDB.file_type == file_type.value
            ).count()
            files_by_type[file_type.value] = count
        
        # Archivos recientes
        recent_files = db.query(FileDB).filter(
            FileDB.user_id == current_user.id
        ).order_by(FileDB.created_at.desc()).limit(5).all()
        
        recent_uploads = []
        for file in recent_files:
            file_info = FileInfo.from_orm(file)
            file_info.download_url = f"/api/files/{file.id}/download"
            recent_uploads.append(file_info)
        
        # Más descargados
        popular_files = db.query(FileDB).filter(
            FileDB.user_id == current_user.id
        ).order_by(FileDB.download_count.desc()).limit(5).all()
        
        most_downloaded = []
        for file in popular_files:
            file_info = FileInfo.from_orm(file)
            file_info.download_url = f"/api/files/{file.id}/download"
            most_downloaded.append(file_info)
        
        return FileStats(
            total_files=total_files,
            total_size=total_size_result,
            files_by_type=files_by_type,
            recent_uploads=recent_uploads,
            most_downloaded=most_downloaded,
            storage_usage={
                "used": total_size_result,
                "limit": MAX_FILE_SIZE * 100,  # Límite simulado
                "percentage": (total_size_result / (MAX_FILE_SIZE * 100)) * 100
            }
        )
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )

@router.post("/cleanup")
async def cleanup_orphaned_files(
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Limpia archivos huérfanos (sin registro en BD)
    """
    try:
        cleaned_files = 0
        freed_space = 0
        
        # Obtener todos los archivos del usuario
        user_files = db.query(FileDB).filter(FileDB.user_id == current_user.id).all()
        registered_paths = {Path(f.file_path) for f in user_files}
        
        # Buscar archivos físicos sin registro
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file() and file_path not in registered_paths:
                # Verificar si el archivo pertenece al usuario (por nombre)
                if current_user.username in file_path.name:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    cleaned_files += 1
                    freed_space += file_size
        
        return {
            "success": True,
            "cleaned_files": cleaned_files,
            "freed_space": freed_space,
            "message": f"Limpieza completada: {cleaned_files} archivos eliminados, {freed_space} bytes liberados"
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error durante la limpieza"
        )

# Funciones auxiliares

async def process_file_background(file_id: int, file_path: Path, file_type: FileType):
    """Procesa un archivo en segundo plano (miniaturas, metadata, etc.)"""
    try:
        # Obtener sesión de base de datos
        from ..database import SessionLocal
        db = SessionLocal()
        
        try:
            file_record = db.query(FileDB).filter(FileDB.id == file_id).first()
            if not file_record:
                return
            
            # Crear miniatura
            thumbnail_path = await file_manager.create_thumbnail(file_path, file_type)
            if thumbnail_path:
                file_record.thumbnail_path = str(thumbnail_path)
            
            # Extraer metadata
            metadata = file_manager.get_file_metadata(file_path, file_type)
            if metadata:
                import json
                file_record.file_meta = json.dumps(metadata)
            
            db.commit()
            logger.info(f"Archivo {file_id} procesado correctamente")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error al procesar archivo {file_id}: {e}")


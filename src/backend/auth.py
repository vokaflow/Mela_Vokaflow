#!/usr/bin/env python3
"""
Módulo de autenticación para VokaFlow
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verifica un token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Dependencias adicionales para autenticación
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, UserDB
from typing import Optional

# Esquema de seguridad
security = HTTPBearer()

class User:
    """Modelo de usuario para respuestas"""
    def __init__(self, id: int, email: str, username: str, full_name: str = None, is_active: bool = True):
        self.id = id
        self.email = email
        self.username = username
        self.full_name = full_name
        self.is_active = is_active

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtiene el usuario actual basado en el token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar el token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Obtener el email del payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active
    )

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Obtiene el usuario actual activo
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Obtiene el usuario actual de forma opcional (sin requerir autenticación)
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        
        email: str = payload.get("sub")
        if email is None:
            return None
            
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if user is None:
            return None
        
        return User(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active
        )
    except Exception:
        return None

# Función para crear un usuario de prueba
def create_test_user(db: Session) -> UserDB:
    """
    Crea un usuario de prueba si no existe
    """
    test_email = "test@vokaflow.com"
    existing_user = db.query(UserDB).filter(UserDB.email == test_email).first()
    
    if not existing_user:
        test_user = UserDB(
            email=test_email,
            username="testuser",
            password_hash=get_password_hash("testpassword"),
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        return test_user
    
    return existing_user

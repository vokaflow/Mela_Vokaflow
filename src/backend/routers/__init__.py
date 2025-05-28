"""
Paquete de routers para la API de VokaFlow.
Este módulo inicializa y expone todos los routers de la aplicación.
"""

from fastapi import APIRouter

# Crear un router ficticio cuando falta el original
def create_dummy_router(name):
    router = APIRouter()

    @router.get("/")
    async def root():
        return {"message": f"Router {name} en construcción"}

    return router

# Intentar importar routers reales, o usar dummies si no existen
try:
    from .auth import router as auth_router
except ImportError:
    auth_router = create_dummy_router("auth")

# Intentar importar el router de Kinect
try:
    from .kinect import router as kinect_router
except ImportError:
    kinect_router = create_dummy_router("kinect")

# Intentar importar el router de Health
try:
    from .health import router as health_router
except ImportError:
    health_router = create_dummy_router("health")

# Asignar todos los routers, reales o dummies
auth = auth_router
users = create_dummy_router("users")
translate = create_dummy_router("translate")
vicky = create_dummy_router("vicky")
tts = create_dummy_router("tts")
stt = create_dummy_router("stt")
voice = create_dummy_router("voice")
conversations = create_dummy_router("conversations")
system = create_dummy_router("system")
system_control = create_dummy_router("system_control")
kinect = kinect_router
health = health_router

# Crear un router principal que incluirá todos los demás
api_router = APIRouter()

# Registrar todos los routers con sus prefijos
api_router.include_router(auth, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users, prefix="/users", tags=["Usuarios"])
api_router.include_router(translate, prefix="/translate", tags=["Traducción"])
api_router.include_router(vicky, prefix="/vicky", tags=["Vicky"])
api_router.include_router(tts, prefix="/tts", tags=["Text-to-Speech"])
api_router.include_router(stt, prefix="/stt", tags=["Speech-to-Text"])
api_router.include_router(voice, prefix="/voice", tags=["Voces"])
api_router.include_router(conversations, prefix="/conversations", tags=["Conversaciones"])
api_router.include_router(system, prefix="/system", tags=["Sistema"])
api_router.include_router(kinect, prefix="/kinect", tags=["Kinect"])
api_router.include_router(health, prefix="/health", tags=["Health"])

# Función para obtener todos los routers
def get_api_router():
    """
    Retorna el router principal con todos los sub-routers incluidos.
    """
    return api_router

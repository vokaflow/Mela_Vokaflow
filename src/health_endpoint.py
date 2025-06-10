# Endpoint de health sin prefijo para compatibilidad con Prometheus
@app.get("/health")
async def health_check_root():
    """Endpoint de health básico para Prometheus/Docker"""
    try:
        from backend.routers.health import comprehensive_health_check
        result = await comprehensive_health_check()
        return result
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 
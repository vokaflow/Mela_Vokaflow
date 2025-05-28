-- Configuración optimizada de PostgreSQL para VokaFlow Messaging
-- Ejecutar como superusuario para configuraciones a nivel de sistema

-- Configuraciones de rendimiento para PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Configuraciones específicas para aplicaciones de mensajería
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;

-- Configuraciones para búsqueda de texto completo
ALTER SYSTEM SET default_text_search_config = 'pg_catalog.spanish';

-- Aplicar configuraciones
SELECT pg_reload_conf();

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Configurar búsqueda de texto completo en español
CREATE TEXT SEARCH CONFIGURATION spanish_unaccent (COPY = spanish);
ALTER TEXT SEARCH CONFIGURATION spanish_unaccent
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, spanish_stem;

-- Crear esquema para mensajería si no existe
CREATE SCHEMA IF NOT EXISTS messaging;

-- Configurar permisos
GRANT USAGE ON SCHEMA messaging TO vokaflow;
GRANT CREATE ON SCHEMA messaging TO vokaflow;

-- Crear tablas optimizadas para mensajería

-- Tabla de usuarios (referencia)
CREATE TABLE IF NOT EXISTS messaging.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url TEXT,
    status VARCHAR(20) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'away', 'busy', 'invisible')),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de conversaciones
CREATE TABLE IF NOT EXISTS messaging.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(20) NOT NULL CHECK (type IN ('private', 'group', 'broadcast', 'channel')),
    title VARCHAR(255),
    description TEXT,
    avatar_url TEXT,
    creator_id UUID NOT NULL REFERENCES messaging.users(id),
    is_encrypted BOOLEAN DEFAULT false,
    encryption_type VARCHAR(20) DEFAULT 'none' CHECK (encryption_type IN ('none', 'transport', 'e2e')),
    encryption_metadata JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    is_archived BOOLEAN DEFAULT false,
    is_muted BOOLEAN DEFAULT false,
    muted_until TIMESTAMPTZ,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de participantes
CREATE TABLE IF NOT EXISTS messaging.participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES messaging.conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES messaging.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'moderator', 'member')),
    permissions JSONB DEFAULT '{}',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    last_read_message_id UUID,
    last_read_at TIMESTAMPTZ,
    is_muted BOOLEAN DEFAULT false,
    muted_until TIMESTAMPTZ,
    notification_settings JSONB DEFAULT '{}',
    UNIQUE(conversation_id, user_id)
);

-- Tabla de mensajes
CREATE TABLE IF NOT EXISTS messaging.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES messaging.conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES messaging.users(id),
    content JSONB NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text' CHECK (content_type IN ('text', 'image', 'video', 'audio', 'file', 'location', 'contact', 'poll', 'system')),
    reply_to_id UUID REFERENCES messaging.messages(id),
    thread_id UUID,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
    is_edited BOOLEAN DEFAULT false,
    is_deleted BOOLEAN DEFAULT false,
    is_encrypted BOOLEAN DEFAULT false,
    encryption_type VARCHAR(20) DEFAULT 'none',
    encryption_metadata JSONB DEFAULT '{}',
    client_id VARCHAR(100),
    mentions UUID[] DEFAULT '{}',
    is_pinned BOOLEAN DEFAULT false,
    is_starred BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ,
    search_vector tsvector,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Tabla de adjuntos
CREATE TABLE IF NOT EXISTS messaging.attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messaging.messages(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('image', 'video', 'audio', 'document', 'other')),
    name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    url TEXT NOT NULL,
    thumbnail_url TEXT,
    mime_type VARCHAR(100),
    size BIGINT,
    width INTEGER,
    height INTEGER,
    duration INTEGER,
    metadata JSONB DEFAULT '{}',
    upload_status VARCHAR(20) DEFAULT 'complete' CHECK (upload_status IN ('uploading', 'complete', 'failed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de reacciones
CREATE TABLE IF NOT EXISTS messaging.reactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messaging.messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES messaging.users(id) ON DELETE CASCADE,
    reaction VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(message_id, user_id, reaction)
);

-- Tabla de estado de entrega
CREATE TABLE IF NOT EXISTS messaging.delivery_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messaging.messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES messaging.users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('sent', 'delivered', 'read')),
    device_id VARCHAR(100),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(message_id, user_id, status)
);

-- Tabla de traducciones
CREATE TABLE IF NOT EXISTS messaging.translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messaging.messages(id) ON DELETE CASCADE,
    target_language VARCHAR(10) NOT NULL,
    translated_content JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    provider VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(message_id, target_language)
);

-- Tabla de presencia
CREATE TABLE IF NOT EXISTS messaging.presence (
    user_id UUID PRIMARY KEY REFERENCES messaging.users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'offline',
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    device_id VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de estado de escritura
CREATE TABLE IF NOT EXISTS messaging.typing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES messaging.conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES messaging.users(id) ON DELETE CASCADE,
    is_typing BOOLEAN DEFAULT false,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '5 seconds',
    UNIQUE(conversation_id, user_id)
);

-- Tabla de dispositivos
CREATE TABLE IF NOT EXISTS messaging.devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES messaging.users(id) ON DELETE CASCADE,
    device_id VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) CHECK (device_type IN ('web', 'mobile', 'desktop', 'tablet')),
    device_name VARCHAR(100),
    push_token TEXT,
    is_active BOOLEAN DEFAULT true,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, device_id)
);

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS messaging.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES messaging.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    data JSONB DEFAULT '{}',
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ÍNDICES OPTIMIZADOS

-- Índices para conversaciones
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_type ON messaging.conversations(type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_creator ON messaging.conversations(creator_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_last_activity ON messaging.conversations(last_activity DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_archived ON messaging.conversations(is_archived) WHERE is_archived = false;

-- Índices para participantes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_conversation ON messaging.participants(conversation_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_user ON messaging.participants(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_role ON messaging.participants(conversation_id, role);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_active ON messaging.participants(conversation_id, user_id) WHERE left_at IS NULL;

-- Índices para mensajes (los más críticos)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_created ON messaging.messages(conversation_id, created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_sender ON messaging.messages(sender_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_reply_to ON messaging.messages(reply_to_id) WHERE reply_to_id IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_thread ON messaging.messages(thread_id) WHERE thread_id IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_status ON messaging.messages(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_deleted ON messaging.messages(is_deleted) WHERE is_deleted = false;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_search ON messaging.messages USING GIN(search_vector);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_mentions ON messaging.messages USING GIN(mentions) WHERE array_length(mentions, 1) > 0;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_expires ON messaging.messages(expires_at) WHERE expires_at IS NOT NULL;

-- Índices para adjuntos
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attachments_message ON messaging.attachments(message_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_attachments_type ON messaging.attachments(type);

-- Índices para reacciones
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reactions_message ON messaging.reactions(message_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reactions_user ON messaging.reactions(user_id);

-- Índices para estado de entrega
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_delivery_status_message ON messaging.delivery_status(message_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_delivery_status_user ON messaging.delivery_status(user_id);

-- Índices para traducciones
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_translations_message_lang ON messaging.translations(message_id, target_language);

-- Índices para presencia
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_presence_status ON messaging.presence(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_presence_last_seen ON messaging.presence(last_seen);

-- Índices para estado de escritura
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_typing_conversation ON messaging.typing_status(conversation_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_typing_expires ON messaging.typing_status(expires_at);

-- Índices para dispositivos
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_devices_user ON messaging.devices(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_devices_active ON messaging.devices(user_id, is_active) WHERE is_active = true;

-- Índices para notificaciones
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user ON messaging.notifications(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_unread ON messaging.notifications(user_id, is_read) WHERE is_read = false;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_priority ON messaging.notifications(priority, created_at);

-- TRIGGERS Y FUNCIONES

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION messaging.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON messaging.users FOR EACH ROW EXECUTE FUNCTION messaging.update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON messaging.conversations FOR EACH ROW EXECUTE FUNCTION messaging.update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messaging.messages FOR EACH ROW EXECUTE FUNCTION messaging.update_updated_at_column();

-- Función para actualizar vector de búsqueda
CREATE OR REPLACE FUNCTION messaging.update_message_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo actualizar si el contenido es de tipo texto
    IF NEW.content_type = 'text' AND NEW.content ? 'text' THEN
        NEW.search_vector := to_tsvector('spanish_unaccent', COALESCE(NEW.content->>'text', ''));
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para vector de búsqueda
CREATE TRIGGER update_message_search_vector 
    BEFORE INSERT OR UPDATE ON messaging.messages 
    FOR EACH ROW EXECUTE FUNCTION messaging.update_message_search_vector();

-- Función para actualizar contador de mensajes
CREATE OR REPLACE FUNCTION messaging.update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE messaging.conversations 
        SET message_count = message_count + 1,
            last_activity = NEW.created_at
        WHERE id = NEW.conversation_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE messaging.conversations 
        SET message_count = message_count - 1
        WHERE id = OLD.conversation_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Trigger para contador de mensajes
CREATE TRIGGER update_conversation_message_count
    AFTER INSERT OR DELETE ON messaging.messages
    FOR EACH ROW EXECUTE FUNCTION messaging.update_conversation_message_count();

-- Función para limpiar estado de escritura expirado
CREATE OR REPLACE FUNCTION messaging.cleanup_expired_typing()
RETURNS void AS $$
BEGIN
    DELETE FROM messaging.typing_status WHERE expires_at < NOW();
END;
$$ language 'plpgsql';

-- Función para limpiar notificaciones expiradas
CREATE OR REPLACE FUNCTION messaging.cleanup_expired_notifications()
RETURNS void AS $$
BEGIN
    DELETE FROM messaging.notifications WHERE expires_at < NOW();
END;
$$ language 'plpgsql';

-- Función para archivar mensajes antiguos
CREATE OR REPLACE FUNCTION messaging.archive_old_messages(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Marcar mensajes como eliminados en lugar de eliminarlos físicamente
    UPDATE messaging.messages 
    SET is_deleted = true, deleted_at = NOW()
    WHERE created_at < NOW() - (retention_days || ' days')::INTERVAL
    AND is_deleted = false;
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ language 'plpgsql';

-- VISTAS ÚTILES

-- Vista para conversaciones con último mensaje
CREATE OR REPLACE VIEW messaging.conversations_with_last_message AS
SELECT 
    c.*,
    m.id as last_message_id,
    m.content as last_message_content,
    m.sender_id as last_message_sender_id,
    m.created_at as last_message_at,
    u.display_name as last_message_sender_name
FROM messaging.conversations c
LEFT JOIN LATERAL (
    SELECT * FROM messaging.messages 
    WHERE conversation_id = c.id 
    AND is_deleted = false
    ORDER BY created_at DESC 
    LIMIT 1
) m ON true
LEFT JOIN messaging.users u ON m.sender_id = u.id;

-- Vista para mensajes con información del remitente
CREATE OR REPLACE VIEW messaging.messages_with_sender AS
SELECT 
    m.*,
    u.username as sender_username,
    u.display_name as sender_display_name,
    u.avatar_url as sender_avatar_url
FROM messaging.messages m
JOIN messaging.users u ON m.sender_id = u.id
WHERE m.is_deleted = false;

-- Vista para estadísticas de conversaciones
CREATE OR REPLACE VIEW messaging.conversation_stats AS
SELECT 
    c.id,
    c.title,
    c.type,
    COUNT(DISTINCT p.user_id) as participant_count,
    COUNT(m.id) as total_messages,
    COUNT(CASE WHEN m.created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as messages_last_24h,
    MAX(m.created_at) as last_message_at
FROM messaging.conversations c
LEFT JOIN messaging.participants p ON c.id = p.conversation_id AND p.left_at IS NULL
LEFT JOIN messaging.messages m ON c.id = m.conversation_id AND m.is_deleted = false
GROUP BY c.id, c.title, c.type;

-- CONFIGURACIÓN DE PARTICIONADO (para alta escala)

-- Particionar tabla de mensajes por fecha (mensual)
-- Esto es opcional y se debe implementar solo si se espera un volumen muy alto

-- CREATE TABLE messaging.messages_y2024m01 PARTITION OF messaging.messages
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- CONFIGURACIÓN DE REPLICACIÓN (para alta disponibilidad)

-- Configurar replicación de lectura si es necesario
-- ALTER SYSTEM SET wal_level = replica;
-- ALTER SYSTEM SET max_wal_senders = 3;
-- ALTER SYSTEM SET wal_keep_segments = 64;

-- CONFIGURACIÓN DE BACKUP

-- Configurar backup automático
-- ALTER SYSTEM SET archive_mode = on;
-- ALTER SYSTEM SET archive_command = 'cp %p /backup/archive/%f';

-- ESTADÍSTICAS Y MANTENIMIENTO

-- Configurar auto-vacuum más agresivo para tablas de alta actividad
ALTER TABLE messaging.messages SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05,
    autovacuum_vacuum_cost_delay = 10
);

ALTER TABLE messaging.delivery_status SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

-- Configurar estadísticas extendidas para mejores planes de consulta
CREATE STATISTICS IF NOT EXISTS messaging.messages_conversation_sender_stats 
ON conversation_id, sender_id FROM messaging.messages;

CREATE STATISTICS IF NOT EXISTS messaging.messages_conversation_created_stats 
ON conversation_id, created_at FROM messaging.messages;

-- Actualizar estadísticas
ANALYZE messaging.conversations;
ANALYZE messaging.messages;
ANALYZE messaging.participants;
ANALYZE messaging.attachments;
ANALYZE messaging.reactions;
ANALYZE messaging.delivery_status;

-- Crear trabajos de mantenimiento programados (requiere pg_cron)
-- SELECT cron.schedule('cleanup-typing', '*/1 * * * *', 'SELECT messaging.cleanup_expired_typing();');
-- SELECT cron.schedule('cleanup-notifications', '0 */6 * * *', 'SELECT messaging.cleanup_expired_notifications();');
-- SELECT cron.schedule('archive-messages', '0 2 * * 0', 'SELECT messaging.archive_old_messages(365);');

COMMIT;

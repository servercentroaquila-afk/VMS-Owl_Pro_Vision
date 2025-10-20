-- Script de inicialización de la base de datos VMS Áquila

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear usuario de aplicación (opcional)
-- CREATE USER vms_app WITH PASSWORD 'vms_app_password';
-- GRANT ALL PRIVILEGES ON DATABASE vmsdb TO vms_app;

-- Configuraciones de la base de datos
ALTER DATABASE vmsdb SET timezone TO 'UTC';

-- Comentarios sobre las tablas
COMMENT ON DATABASE vmsdb IS 'Base de datos del sistema VMS Áquila - Gestión de Video';

-- Las tablas se crearán automáticamente por SQLAlchemy
-- Este archivo se puede usar para configuraciones adicionales o datos iniciales

-- Crear usuario
CREATE USER ccb_user WITH PASSWORD 'ccb_secure_password_2025';

-- Crear base de datos de producción
CREATE DATABASE ccb_production OWNER ccb_user;
GRANT ALL PRIVILEGES ON DATABASE ccb_production TO ccb_user;

-- Crear base de datos de desarrollo
CREATE DATABASE ccb_development OWNER ccb_user;
GRANT ALL PRIVILEGES ON DATABASE ccb_development TO ccb_user;

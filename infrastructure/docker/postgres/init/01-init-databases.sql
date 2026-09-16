-- Vajra Core - PostgreSQL Initialization Script
-- Phase 0.5 Foundation

-- Create additional databases if needed
-- Main database is created automatically by POSTGRES_DB environment variable

-- Create Keycloak database (for authentication when enabled)
CREATE DATABASE keycloak;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE keycloak TO vajra;

-- Create extensions for main database
\c vajra_core;

-- Enable UUID extension for better ID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for text search capabilities (useful for configuration search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable pgcrypto for cryptographic functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create initial metadata
CREATE TABLE IF NOT EXISTS migration_history (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO migration_history (version, description) 
VALUES ('0.5.0', 'Phase 0.5 Foundation - PostgreSQL initialization');

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Vajra Core PostgreSQL initialization completed successfully';
END $$;

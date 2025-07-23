-- Initial database setup for Baobab AI
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
-- SELECT 'CREATE DATABASE baobab_ai' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'baobab_ai')\gexec

-- Connect to the baobab_ai database
\c baobab_ai;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by Alembic migrations, but we can add them here for reference

-- Example: Full-text search index for knowledge base
-- CREATE INDEX IF NOT EXISTS idx_knowledge_base_content_fts 
-- ON knowledge_base USING gin(to_tsvector('english', content));

-- Example: Index for user lookups
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Insert sample data (optional)
-- This can be used for initial setup or demo purposes

-- Sample African countries for reference
CREATE TABLE IF NOT EXISTS african_countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO african_countries (name, code, region) VALUES
    ('Nigeria', 'NGA', 'West Africa'),
    ('Kenya', 'KEN', 'East Africa'),
    ('South Africa', 'ZAF', 'Southern Africa'),
    ('Ghana', 'GHA', 'West Africa'),
    ('Rwanda', 'RWA', 'East Africa'),
    ('Morocco', 'MAR', 'North Africa'),
    ('Egypt', 'EGY', 'North Africa'),
    ('Ethiopia', 'ETH', 'East Africa'),
    ('Uganda', 'UGA', 'East Africa'),
    ('Tanzania', 'TZA', 'East Africa'),
    ('Senegal', 'SEN', 'West Africa'),
    ('Ivory Coast', 'CIV', 'West Africa'),
    ('Cameroon', 'CMR', 'Central Africa'),
    ('Botswana', 'BWA', 'Southern Africa'),
    ('Tunisia', 'TUN', 'North Africa')
ON CONFLICT DO NOTHING;

-- Sample industries for reference
CREATE TABLE IF NOT EXISTS industries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO industries (name, description) VALUES
    ('Fintech', 'Financial technology and digital payments'),
    ('E-commerce', 'Online retail and marketplace platforms'),
    ('AgriTech', 'Agricultural technology and farming solutions'),
    ('HealthTech', 'Healthcare technology and medical solutions'),
    ('EdTech', 'Educational technology and learning platforms'),
    ('CleanTech', 'Clean energy and environmental technology'),
    ('Logistics', 'Transportation and supply chain solutions'),
    ('Telecommunications', 'Communication technology and services'),
    ('Entertainment', 'Media, gaming, and entertainment platforms'),
    ('Real Estate', 'Property technology and real estate services')
ON CONFLICT DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant permissions to the baobab_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO baobab_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO baobab_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO baobab_user;

-- Set default permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO baobab_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO baobab_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO baobab_user;
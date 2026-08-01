-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop table if exists during re-initialization
DROP TABLE IF EXISTS destinations;

-- Table for storing relational metadata, textual descriptions, and embeddings
CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,          -- e.g., 'waterfalls', 'temples', 'beaches'
    district VARCHAR(100) NOT NULL,
    entrance_fee NUMERIC(10, 2) DEFAULT 0.00,
    accessibility VARCHAR(100),
    trekking_difficulty VARCHAR(50),
    description TEXT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    
    -- Embeddings
    text_embedding VECTOR(384),              -- Dimension for sentence-transformers/all-MiniLM-L6-v2
    image_embedding VECTOR(512)              -- Dimension for openai/clip-vit-base-patch32
);

-- HNSW Indexes for fast Cosine Distance (<=>) vector similarity search
CREATE INDEX idx_dest_text_embedding ON destinations 
USING hnsw (text_embedding vector_cosine_ops);

CREATE INDEX idx_dest_image_embedding ON destinations 
USING hnsw (image_embedding vector_cosine_ops);
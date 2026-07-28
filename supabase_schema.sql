-- Habilitar extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla para almacenar metadatos de los artículos
CREATE TABLE IF NOT EXISTS papers_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo TEXT NOT NULL,
    autores TEXT[],
    abstract TEXT,
    url_pdf TEXT,
    tecnologia TEXT,
    fecha_publicacion DATE,
    procesado BOOLEAN DEFAULT false
);

-- Tabla para almacenar los embeddings de los chunks de texto
CREATE TABLE IF NOT EXISTS papers_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID REFERENCES papers_metadata(id) ON DELETE CASCADE,
    contenido_chunk TEXT NOT NULL,
    vector_embedding vector(768) NOT NULL,
    numero_pagina INT
);

-- Índice HNSW para búsqueda vectorial rápida
CREATE INDEX IF NOT EXISTS papers_embeddings_hnsw_idx ON papers_embeddings USING hnsw (vector_embedding vector_cosine_ops);

-- Tabla para almacenar menciones sociales / sentiment analysis
CREATE TABLE IF NOT EXISTS social_listening (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plataforma TEXT,
    contenido TEXT,
    sentimiento FLOAT,
    engagement_score INT,
    tecnologia TEXT,
    fecha TIMESTAMP DEFAULT now()
);

-- Tabla para almacenar parámetros del modelo matemático de adopción
CREATE TABLE IF NOT EXISTS model_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tecnologia TEXT,
    modelo_tipo TEXT,
    param_p1 FLOAT,
    param_q1 FLOAT,
    param_m1 FLOAT,
    param_p2 FLOAT DEFAULT 0.0,
    param_q2 FLOAT DEFAULT 0.0,
    param_m2 FLOAT DEFAULT 0.0,
    param_q12 FLOAT DEFAULT 0.0,
    r_cuadrado FLOAT,
    fecha_calculo TIMESTAMP DEFAULT now()
);

-- Tabla para almacenar datos históricos de adopción (ej. conteo de publicaciones/patentes anuales)
CREATE TABLE IF NOT EXISTS historical_adoption (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tecnologia TEXT,
    anio INT,
    adopcion_anual BIGINT, -- Nuevos adoptantes (ej. publicaciones ese año)
    adopcion_acumulada BIGINT, -- Adoptantes acumulados hasta ese año
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(tecnologia, anio)
);

-- Función para búsqueda de similitud (Cosine Similarity)
CREATE OR REPLACE FUNCTION match_chunks (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  tecnologia_filter text DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  paper_id UUID,
  contenido_chunk TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    pe.id,
    pe.paper_id,
    pe.contenido_chunk,
    1 - (pe.vector_embedding <=> query_embedding) AS similarity
  FROM papers_embeddings pe
  JOIN papers_metadata pm ON pe.paper_id = pm.id
  WHERE 1 - (pe.vector_embedding <=> query_embedding) > match_threshold
    AND (tecnologia_filter IS NULL OR pm.tecnologia = tecnologia_filter OR pm.tecnologia = 'general' OR pm.tecnologia IS NULL)
  ORDER BY pe.vector_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Tabla para almacenar el análisis cualitativo generado por IA
CREATE TABLE IF NOT EXISTS qualitative_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tecnologia TEXT UNIQUE NOT NULL,
    analisis TEXT NOT NULL,
    fecha_analisis TIMESTAMP DEFAULT now()
);

-- Tabla para almacenar el pronóstico de consenso generado por IA
CREATE TABLE IF NOT EXISTS consensus_forecast (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tecnologia TEXT UNIQUE NOT NULL,
    consenso TEXT NOT NULL,
    fecha_calculo TIMESTAMP DEFAULT now()
);

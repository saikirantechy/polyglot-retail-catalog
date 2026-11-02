-- Run in AlloyDB Studio after confirming the extension support/permissions.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS google_ml_integration;

ALTER TABLE products_core_table
    ADD COLUMN IF NOT EXISTS img_embeddings vector(1408);

-- Verify extension and column state.
SELECT extname
FROM pg_extension
WHERE extname IN ('vector', 'google_ml_integration');

SELECT column_name, udt_name
FROM information_schema.columns
WHERE table_name = 'products_core_table'
  AND column_name = 'img_embeddings';

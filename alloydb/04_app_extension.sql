-- Run in AlloyDB Studio after 01_schema.sql.
-- Adds the optional storefront columns used by the Flask application.
ALTER TABLE products_core_table
    ADD COLUMN IF NOT EXISTS category VARCHAR(80) DEFAULT 'Uncategorised',
    ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '',
    ADD COLUMN IF NOT EXISTS image_url TEXT DEFAULT '',
    ADD COLUMN IF NOT EXISTS visual_tags TEXT[] DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_products_category
    ON products_core_table (category);

CREATE INDEX IF NOT EXISTS idx_products_visual_tags
    ON products_core_table USING GIN (visual_tags);

SELECT column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_schema = current_schema()
  AND table_name = 'products_core_table'
ORDER BY ordinal_position;

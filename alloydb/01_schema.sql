-- Run in AlloyDB Studio, database: postgres
CREATE TABLE IF NOT EXISTS products_core_table (
    product_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_products_core_sku
    ON products_core_table (sku);

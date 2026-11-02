-- Run in AlloyDB Studio.
SELECT COUNT(*) AS total_products
FROM products_core_table;

SELECT
    column_name,
    data_type,
    udt_name,
    is_nullable
FROM information_schema.columns
WHERE table_schema = current_schema()
  AND table_name = 'products_core_table'
ORDER BY ordinal_position;

SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = current_schema()
  AND tablename = 'products_core_table';

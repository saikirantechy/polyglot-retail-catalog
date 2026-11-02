-- Optional sample catalog matching app/data/seed_products.json.
-- Run in AlloyDB Studio after 01_schema.sql and 04_app_extension.sql.
INSERT INTO products_core_table
    (product_id, name, sku, price, stock, category, description, visual_tags)
VALUES
    ('11111111-1111-4111-8111-111111111101', 'Aurora Wireless Headphones', 'AUD-1001', 249.00, 24, 'Audio',
     'Over-ear noise-cancelling headphones with 32-hour battery life and a lightweight aluminium frame.',
     ARRAY['over-ear', 'wireless', 'noise-cancelling', 'black', 'premium']),
    ('11111111-1111-4111-8111-111111111102', 'Nimbus Earbuds Pro', 'AUD-1002', 129.00, 80, 'Audio',
     'Compact wireless earbuds with adaptive noise cancellation and a pocket-sized charging case.',
     ARRAY['in-ear', 'wireless', 'noise-cancelling', 'white', 'compact']),
    ('11111111-1111-4111-8111-111111111103', 'Pulse Smartwatch Series 5', 'WEA-2001', 299.00, 15, 'Wearables',
     'AMOLED smartwatch with continuous heart-rate tracking, GPS and a seven-day battery.',
     ARRAY['smartwatch', 'fitness', 'amoled', 'black', 'premium']),
    ('11111111-1111-4111-8111-111111111104', 'Drift Fitness Band', 'WEA-2002', 79.00, 0, 'Wearables',
     'Lightweight fitness band for step, sleep and workout tracking with a slim teal strap.',
     ARRAY['fitness', 'band', 'lightweight', 'teal', 'budget']),
    ('11111111-1111-4111-8111-111111111105', 'Halo Desk Lamp', 'HOM-3001', 89.00, 42, 'Home',
     'Minimal LED desk lamp with adjustable colour temperature and a touch dimmer.',
     ARRAY['lamp', 'minimal', 'led', 'white', 'desk']),
    ('11111111-1111-4111-8111-111111111106', 'Terra Ceramic Planter', 'HOM-3002', 34.50, 120, 'Home',
     'Matte ceramic planter with a drainage tray for small indoor plants.',
     ARRAY['planter', 'ceramic', 'matte', 'green', 'decor']),
    ('11111111-1111-4111-8111-111111111107', 'Vista Mirrorless Camera', 'PHO-4001', 1299.00, 6, 'Photography',
     '24 MP mirrorless camera with 4K video, in-body stabilisation and a bright OLED viewfinder.',
     ARRAY['camera', 'mirrorless', '4k', 'black', 'premium']),
    ('11111111-1111-4111-8111-111111111108', 'Orbit Action Camera', 'PHO-4002', 399.00, 18, 'Photography',
     'Rugged waterproof action camera with horizon lock and a wide-angle lens.',
     ARRAY['camera', 'action', 'waterproof', 'rugged', 'outdoor']),
    ('11111111-1111-4111-8111-111111111109', 'Vertex Mechanical Keyboard', 'GAM-5001', 159.00, 33, 'Gaming',
     'Hot-swappable mechanical keyboard with per-key RGB lighting and a gasket-mounted plate.',
     ARRAY['keyboard', 'mechanical', 'rgb', 'black', 'gaming']),
    ('11111111-1111-4111-8111-111111111110', 'Nova Gaming Mouse', 'GAM-5002', 69.00, 64, 'Gaming',
     'Lightweight wireless gaming mouse with a 26K optical sensor and 90-hour battery.',
     ARRAY['mouse', 'wireless', 'lightweight', 'white', 'gaming']),
    ('11111111-1111-4111-8111-111111111111', 'Summit Trail Backpack', 'ACC-6001', 119.00, 27, 'Accessories',
     'Water-resistant 28-litre hiking backpack with a ventilated back panel and laptop sleeve.',
     ARRAY['backpack', 'outdoor', 'water-resistant', 'olive', 'travel']),
    ('11111111-1111-4111-8111-111111111112', 'Slate Laptop Sleeve', 'ACC-6002', 45.00, 95, 'Accessories',
     'Felt laptop sleeve with a magnetic closure and a slim accessory pocket.',
     ARRAY['sleeve', 'laptop', 'felt', 'grey', 'minimal'])
ON CONFLICT (sku) DO NOTHING;

SELECT COUNT(*) AS total_products FROM products_core_table;

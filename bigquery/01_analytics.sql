-- Create the dataset ecommerce_analytics in the US multi-region
-- using BigQuery Console or bq CLI first.
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.ecommerce_analytics.user_product_interactions` (
    user_id STRING DEFAULT 'any user',
    product_id STRING,
    interaction_score INT64
);

-- Example validation query:
SELECT COUNT(*) AS interaction_rows
FROM `YOUR_PROJECT_ID.ecommerce_analytics.user_product_interactions`;

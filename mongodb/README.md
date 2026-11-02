# MongoDB Atlas layout

Create the database `ecommerce_db` (or set `MONGODB_DB`) with two collections.

## `product_details_collection`

Flexible attributes keyed by `sku` or `product_id`.

```json
{
  "sku": "AUD-1001",
  "product_id": "11111111-1111-4111-8111-111111111101",
  "attributes": {
    "color": "Midnight Black",
    "material": "Aluminium and memory foam",
    "battery_hours": 32,
    "features": ["Active noise cancellation", "Multipoint pairing", "Fold-flat case"]
  }
}
```

Create an index:

```javascript
db.product_details_collection.createIndex({ sku: 1 }, { unique: true });
```

## `user_interactions_collection`

Interaction events written by the Flask app.

```json
{
  "user_id": "demo-alice",
  "product_id": "11111111-1111-4111-8111-111111111101",
  "event_type": "purchase",
  "score": 5,
  "created_at": "2026-01-01T00:00:00Z"
}
```

Create indexes:

```javascript
db.user_interactions_collection.createIndex({ product_id: 1, created_at: -1 });
db.user_interactions_collection.createIndex({ user_id: 1, created_at: -1 });
```

## Security

- Use a least-privilege database user limited to `ecommerce_db`.
- Restrict network access to known CIDRs; do not use `0.0.0.0/0` outside a lab.
- Store `MONGODB_URI` in Secret Manager for deployed services.
- Keep exports containing real user data out of Git.

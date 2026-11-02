# Architecture notes

## Data ownership

| Store | Owns | Typical access |
|---|---|---|
| AlloyDB | Product identity, SKU, price, stock, vector | Transactional SQL and vector similarity |
| MongoDB Atlas | Flexible attributes, product metadata, interactions | Document queries and writes |
| Cloud Storage | Product image objects | Object URL / controlled access |
| BigQuery | Aggregated interaction and analytical data | SQL analytics |
| MCP Toolbox | Tool definitions and source connectivity | Agent-facing database tools |

## Example request flow

1. User asks for products visually similar to a reference item and excludes an attribute.
2. Agent selects the appropriate Toolbox tools.
3. AlloyDB finds visually similar products and checks current stock.
4. MongoDB filters flexible attributes such as material and product features.
5. BigQuery supplies aggregated review/interaction insights when available.
6. Agent combines results and explains the evidence.

The agent should not claim that reviews or interactions exist unless the corresponding dataset has been populated and queried.

# Troubleshooting

## SQL pasted into Cloud Shell

SQL statements such as `CREATE TABLE`, `INSERT` and `SELECT` must run in AlloyDB Studio, not Bash. Cloud Shell is for commands such as `gcloud`, `git`, `cat`, `sed` and `curl`.

## Product count is zero

1. Confirm the correct project, cluster and database.
2. Open AlloyDB Studio and authenticate to `postgres`.
3. Run the INSERT statement from the upstream `alloydb_insert_queries.sql` file in a new Studio query tab.
4. Run `SELECT COUNT(*) FROM products_core_table;`.
5. Do not rerun the INSERT after it succeeds; unique SKU constraints will reject duplicates.

## Environment variables disappeared

Cloud Shell exports are session-local. Re-export project, project number, region and bucket after reconnecting. See `scripts/set-env.sh`.

## MCP Toolbox exits with segmentation fault

A segmentation fault occurs before the HTTP server binds to the preview port. Web Preview then reports that it cannot connect. Check architecture (`uname -m`), binary type (`file ~/toolbox`), binary integrity and the version-specific installation instructions. If the local binary continues to crash, use the official versioned container image or supported deployment path. Do not debug the browser preview until the server starts successfully.

## Web Preview cannot connect

Confirm the server is still running and listening on the selected port. Use `curl -i http://127.0.0.1:5000/` from a second terminal. A refused connection means the process is not listening.

## Embeddings are zero

Confirm that product records exist, product image objects are in the configured bucket, AlloyDB service-agent permissions are correct, the extensions and vector column exist, and the generated SQL contains the correct bucket name.

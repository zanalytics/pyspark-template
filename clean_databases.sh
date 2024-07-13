#!/bin/bash
set -e

# Array of files and directories to remove
to_remove=(
    "data/bronze.db"
    "data/silver.db"
    "data/gold.db"
    "derby.log"
    "metastore_db"
)

# Loop through the array and remove each item
for item in "${to_remove[@]}"; do
    rm -rf "$item"
done

# Execute the original command
exec "$@"

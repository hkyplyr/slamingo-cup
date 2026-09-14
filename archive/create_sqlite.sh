#!/bin/bash
TARGET_DIR="./archive" && DB_NAME="slamingo_cup.db"

[ -d "$TARGET_DIR" ] || { echo "❌ Error: Could not find directory '$TARGET_DIR'"; exit 1; }
[ -f "$DB_NAME" ] && rm "$DB_NAME" && echo "🧹 Removed old database."

echo "🚀 Building database..."
find "$TARGET_DIR" -name "*.json" -type f | while read -r f; do
    t=$(basename "$f" .json)
    echo "📂 $f -> [$t]"
    sqlite-utils insert "$DB_NAME" "$t" "$f" --alter --silent
done

echo "⚡ Creating database indexes..."

sqlite-utils create-index "$DB_NAME" managers name
sqlite-utils create-index "$DB_NAME" players sleeper_id

sqlite-utils create-index "$DB_NAME" selected_positions season week manager
sqlite-utils create-index "$DB_NAME" player_stats season week sleeper_id
sqlite-utils create-index "$DB_NAME" weekly_results season week manager

echo "✅ Database built and indexed successfully!"

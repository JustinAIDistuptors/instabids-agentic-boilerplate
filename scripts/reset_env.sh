#!/bin/bash
#
# Reset development environment for InstaBids
# Clears caches and reinstalls dependencies
#

set -e

echo "🧹 Cleaning Python environment..."

# Clear Poetry cache
echo "Clearing Poetry cache..."
poetry cache clear pypi --all 2>/dev/null || true

# Remove virtual environment
if [ -d ".venv" ]; then
    echo "Removing .venv directory..."
    rm -rf .venv
fi

# Clear ADK model cache
if [ -f "$HOME/.cache/adk/model_catalog.json" ]; then
    echo "Clearing ADK model cache..."
    rm -f "$HOME/.cache/adk/model_catalog.json"
fi

# Clear Python cache
echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Regenerate lock file
echo "Regenerating Poetry lock file..."
poetry lock --no-update

# Install dependencies
echo "Installing dependencies..."
poetry install --sync

# Clear Supabase cache if exists
if [ -d ".supabase" ]; then
    echo "Clearing Supabase cache..."
    rm -rf .supabase/.branches
    rm -rf .supabase/.temp
fi

echo "✅ Environment reset complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and configure"
echo "2. Run 'supabase start' to start local database"
echo "3. Run 'poetry run adk web' to start the ADK dev UI"
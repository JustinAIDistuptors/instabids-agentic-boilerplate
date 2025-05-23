# Reset development environment for InstaBids (Windows)
# Clears caches and reinstalls dependencies

Write-Host "🧹 Cleaning Python environment..." -ForegroundColor Green

# Clear Poetry cache
Write-Host "Clearing Poetry cache..."
try {
    poetry cache clear pypi --all 2>$null
} catch {
    Write-Host "Poetry cache already clear" -ForegroundColor Yellow
}

# Remove virtual environment
if (Test-Path ".venv") {
    Write-Host "Removing .venv directory..."
    Remove-Item -Recurse -Force .venv
}

# Clear ADK model cache
$adkCache = "$env:USERPROFILE\.cache\adk\model_catalog.json"
if (Test-Path $adkCache) {
    Write-Host "Clearing ADK model cache..."
    Remove-Item $adkCache -ErrorAction SilentlyContinue
}

# Clear Python cache
Write-Host "Clearing Python cache..."
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue

# Regenerate lock file
Write-Host "Regenerating Poetry lock file..."
poetry lock --no-update

# Install dependencies
Write-Host "Installing dependencies..."
poetry install --sync

# Clear Supabase cache if exists
if (Test-Path ".supabase") {
    Write-Host "Clearing Supabase cache..."
    Remove-Item -Recurse -Force ".supabase\.branches" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force ".supabase\.temp" -ErrorAction SilentlyContinue
}

Write-Host "✅ Environment reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy .env.template to .env and configure"
Write-Host "2. Run 'supabase start' to start local database"
Write-Host "3. Run 'poetry run adk web' to start the ADK dev UI"
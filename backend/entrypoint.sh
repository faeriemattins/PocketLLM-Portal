#!/bin/sh
set -e

# Run from /app so download_model.py writes to /app/models
cd /app || exit 1

# If models directory doesn't exist or is empty, download default models
if [ ! -d "models" ] || [ -z "$(ls -A models 2>/dev/null)" ]; then
  if [ -f "download_model.py" ]; then
    echo "Models directory is empty. Running download_model.py to fetch default models."
    # Provide a non-interactive 'A' (Download All) to the script
    python download_model.py <<'EOF'
A
EOF
  else
    echo "Models directory is empty and download_model.py not found. Skipping model download."
    echo "Please ensure models are in the ./models volume or run download_model.py manually."
  fi
else
  echo "Models directory not empty; skipping automatic download."
fi

# Exec the app (use exec so signals are forwarded)
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000

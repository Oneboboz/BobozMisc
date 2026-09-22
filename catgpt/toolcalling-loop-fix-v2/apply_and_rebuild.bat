@echo off
setlocal
echo ==========================================
echo CatGPT Tool Calling Fix V2
echo ==========================================
echo.

python patch_toolcalling.py
if errorlevel 1 (
  echo [FAILED] Patch failed.
  pause
  exit /b 1
)

echo.
echo [OK] Rebuilding CatGPT...
docker compose build --no-cache
if errorlevel 1 (
  echo [FAILED] Docker build failed.
  pause
  exit /b 1
)

echo.
echo [OK] Restarting CatGPT...
docker compose up -d
docker compose ps
pause

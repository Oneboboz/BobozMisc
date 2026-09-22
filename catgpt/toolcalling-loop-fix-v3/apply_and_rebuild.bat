@echo off
setlocal
python patch_toolcalling_v3.py
if errorlevel 1 (
  echo [FAILED] V3 patch failed.
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

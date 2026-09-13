@echo off
setlocal
cd /d "%~dp0.."
uv run python -m voice_desktop_pet.player --actions-dir assets\packs\mint-assistant\actions --initial-action idle --demo
endlocal

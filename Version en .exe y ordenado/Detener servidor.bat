@echo off
echo 🛑 DETENIENDO SERVIDOR EN PUERTO 8000...
echo.

REM Encontrar PID del proceso usando puerto 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo 🎯 Deteniendo proceso %%a...
        taskkill /PID %%a /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ Proceso %%a detenido
        ) else (
            echo ❌ No se pudo detener proceso %%a
        )
    )
)

echo.
echo 🔒 Proceso completado. Puerto 8000 liberado.
pause
@echo off
set PORT=8000
set RULE_NAME=Servidor_HTTP_Python

echo Agregando regla de Firewall para permitir el puerto %PORT%...

netsh advfirewall firewall add rule name="%RULE_NAME%" dir=in action=allow protocol=TCP localport=%PORT% enable=yes profile=any

echo ---
echo ✅ Puerto %PORT% abierto correctamente en el Firewall.
pause

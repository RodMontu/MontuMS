#!/bin/bash
# Runner V5 (v2): sube motor viejo/nuevo + arnes al /tmp del contenedor (NUNCA /app), ejecuta y limpia. Solo lectura.
set -u
ssh TO 'cat /c/Users/OptiFierro/Desktop/optifierro/backend/motor_v2.py' > /tmp/mv_old.py
ssh TO 'cat /c/Users/OptiFierro/Desktop/optifierro_b42/backend/motor_v2.py' > /tmp/mv_new.py
ssh TO 'MSYS_NO_PATHCONV=1 docker exec optifierro-backend mkdir -p /tmp/mv/old /tmp/mv/new'
push() { ssh TO "MSYS_NO_PATHCONV=1 docker exec -i optifierro-backend sh -c 'cat > $2'" < "$1"; }
push /tmp/mv_old.py /tmp/mv/old/motor_v2.py
push /tmp/mv_new.py /tmp/mv/new/motor_v2.py
push /tmp/arnes_v5_repro.py /tmp/mv/arnes_v5_repro.py
ssh TO 'MSYS_NO_PATHCONV=1 docker exec -e OPENSSL_CONF=/app/openssl_legacy.cnf -e MOTOR_BASE_DIR=/app -w /app optifierro-backend python3 /tmp/mv/arnes_v5_repro.py' > /tmp/v5_arnes_full.txt 2>&1
grep -E "^###|^VIEJO|^NUEVO|^FIN|Traceback|Error" /tmp/v5_arnes_full.txt | cut -c1-1100
ssh TO 'MSYS_NO_PATHCONV=1 docker exec optifierro-backend rm -rf /tmp/mv' && echo "limpieza ok"

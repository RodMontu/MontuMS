#!/bin/bash
# Runner determinismo V5. Solo lectura; todo en /tmp del contenedor (nunca /app); limpia al final.
set -u
push() { ssh TO "MSYS_NO_PATHCONV=1 docker exec -i optifierro-backend sh -c 'cat > $2'" < "$1"; }
ssh TO 'MSYS_NO_PATHCONV=1 docker exec optifierro-backend mkdir -p /tmp/mv/old /tmp/mv/new'
push /tmp/mv_old.py /tmp/mv/old/motor_v2.py
push /tmp/mv_new.py /tmp/mv/new/motor_v2.py
push /tmp/arnes_v5_det.py /tmp/mv/det.py
E='-e OPENSSL_CONF=/app/openssl_legacy.cnf -e MOTOR_BASE_DIR=/app -w /app'
ssh TO "MSYS_NO_PATHCONV=1 docker exec $E optifierro-backend python3 /tmp/mv/det.py dump" 2>&1 | tail -1 | cut -c1-300
for seed in 1 2 3 1; do
  ssh TO "MSYS_NO_PATHCONV=1 docker exec -e PYTHONHASHSEED=$seed $E optifierro-backend python3 /tmp/mv/det.py run" 2>&1 | grep "^seed="
done
ssh TO 'MSYS_NO_PATHCONV=1 docker exec optifierro-backend rm -rf /tmp/mv' && echo "limpieza ok"

# V1 — HEBRAS-01 — Fotos ANTES/DESPUES (23-09-2026)
Fuente: contenedor optifierro-backend, DB real optifierro_v2.db (solo lectura), Excel real. DESPUES = motor con parche cargado desde /tmp del contenedor (servicio desplegado NO tocado). Formato hebras: diametros 8,10,12,16,18,22,25,28,32,36. En SQLite 0/None = sin dato -> default 1.

## ANTES (motor desplegado hoy)
```
Pseudo-terminal will not be allocated because stdin is not a terminal.
SUC|MAQUINA|SQLITE(8,10,12,16,18,22,25,28,32,36)|MOTOR_HOY(idem, default 1)|ESTADO
Calama|Carro de Corte|[2, 2, 2, 2, None, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Calama|COIL 14|[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|COIL 14 M|[1, 1, 1, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|Cortadora Manual|[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|Dobladoras|[0, 0, 1, 0, 1, 1, 1, 1, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|EURA 16|[0, 1, 1, 1, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|EURA 20_2|[0, 2, 1, 1, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Calama|Robomaster 60|[0, 0, 0, 0, 1, 1, 1, 1, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|LINEA DE CORTE|[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|FORMULA 12|[2, 2, 1, 0, 0, 0, 0, 0, 0, 0]|[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|Curvadora CER40 1 Schnell|[0, 0, 0, 2, 2, 1, 1, 3, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|Dobladora Tecmor S40 1|[0, 0, 0, 2, 2, 2, 1, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|Dobladora Tecmor S40 2|[0, 0, 0, 2, 2, 2, 1, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|EURA 16|[2, 2, 2, 1, 0, 0, 0, 0, 0, 0]|[2, 2, 2, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|EURA 20_1|[0, 0, 2, 2, 0, 0, 0, 0, 0, 0]|[1, 2, 2, 2, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|EURA 20_3|[2, 2, 2, 2, None, 0, 0, 0, 0, 0]|[1, 1, 2, 1, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|FP-LC|[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|LINEA DE CORTE|[0, 0, 0, 15, 10, 10, 8, 7, 3, 2]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|PRIMA 3D|[2, 2, 1, 0, 0, 0, 0, 0, 0, 0]|[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|Robomaster 55|[0, 0, 0, 2, 2, 2, 2, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Cerrillos|Robomaster 60|[0, 0, 0, 2, 2, 2, 2, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Cortadora Manual|[2, 2, 2, 2, None, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Curvadora 1|[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Curvadora 2|[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Dobladora 2|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Dobladora 3|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Dobladora 4|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|ESTRIBADORA TJK 1|[2, 2, 1, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|ESTRIBADORA TJK 2|[2, 2, 1, None, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
Coronel|Linea Corte Coronel|[10, 10, 6, 3, 3, 1, 1, 1, 1, 1]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|DIFF
filas DIFF: 19
claves hebras_x_maquina en motor: 92
maquinas en motor por sucursal:
  Calama ['COIL 14', 'COIL 14 M', 'Carro de Corte', 'Dobladoras', 'EURA 16', 'EURA 20_2', 'Robomaster 60']
  Cerrillos ['Curvadora CER40 1 Schnell', 'Dobladora Tecmor S40 1', 'Dobladora Tecmor S40 2', 'EURA 16', 'EURA 20_1', 'EURA 20_3', 'FORMULA 12', 'LINEA DE CORTE', 'PRIMA 3D', 'Robomaster 55', 'Robomaster 60']
  Coronel ['Cortadora Manual', 'Curvadora 1', 'Dobladora 2', 'Dobladora 3', 'ESTRIBADORA TJK 1', 'ESTRIBADORA TJK 2', 'Linea Corte Coronel']
```

## DESPUES (motor con parche) + duraciones
```
== A) FOTO DESPUES (motor con parche, DB real) ==
SUC|MAQUINA|SQLITE|MOTOR_NUEVO|ESTADO
Calama|Carro de Corte|[2, 2, 2, 2, None, 0, 0, 0, 0, 0]|[2, 2, 2, 2, 1, 1, 1, 1, 1, 1]|ok
Calama|COIL 14|[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|COIL 14 M|[1, 1, 1, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|Cortadora Manual|[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|Dobladoras|[0, 0, 1, 0, 1, 1, 1, 1, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|EURA 16|[0, 1, 1, 1, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|EURA 20_2|[0, 2, 1, 1, 0, 0, 0, 0, 0, 0]|[1, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|Robomaster 60|[0, 0, 0, 0, 1, 1, 1, 1, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Calama|LINEA DE CORTE|[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|FORMULA 12|[2, 2, 1, 0, 0, 0, 0, 0, 0, 0]|[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|Curvadora CER40 1 Schnell|[0, 0, 0, 2, 2, 1, 1, 3, 1, 1]|[1, 1, 1, 2, 2, 1, 1, 3, 1, 1]|ok
Cerrillos|Dobladora Tecmor S40 1|[0, 0, 0, 2, 2, 2, 1, 1, 1, 1]|[1, 1, 1, 2, 2, 2, 1, 1, 1, 1]|ok
Cerrillos|Dobladora Tecmor S40 2|[0, 0, 0, 2, 2, 2, 1, 1, 1, 1]|[1, 1, 1, 2, 2, 2, 1, 1, 1, 1]|ok
Cerrillos|EURA 16|[2, 2, 2, 1, 0, 0, 0, 0, 0, 0]|[2, 2, 2, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|EURA 20_1|[0, 0, 2, 2, 0, 0, 0, 0, 0, 0]|[1, 1, 2, 2, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|EURA 20_3|[2, 2, 2, 2, None, 0, 0, 0, 0, 0]|[2, 2, 2, 2, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|FP-LC|[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]|[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|LINEA DE CORTE|[0, 0, 0, 15, 10, 10, 8, 7, 3, 2]|[1, 1, 1, 15, 10, 10, 8, 7, 3, 2]|ok
Cerrillos|PRIMA 3D|[2, 2, 1, 0, 0, 0, 0, 0, 0, 0]|[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Cerrillos|Robomaster 55|[0, 0, 0, 2, 2, 2, 2, 1, 1, 1]|[1, 1, 1, 2, 2, 2, 2, 1, 1, 1]|ok
Cerrillos|Robomaster 60|[0, 0, 0, 2, 2, 2, 2, 1, 1, 1]|[1, 1, 1, 2, 2, 2, 2, 1, 1, 1]|ok
Coronel|Cortadora Manual|[2, 2, 2, 2, None, 0, 0, 0, 0, 0]|[2, 2, 2, 2, 1, 1, 1, 1, 1, 1]|ok
Coronel|Curvadora 1|[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]|[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]|ok
Coronel|Curvadora 2|[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]|[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]|ok
Coronel|Dobladora 2|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|ok
Coronel|Dobladora 3|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|ok
Coronel|Dobladora 4|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|[10, 8, 6, 3, 3, 2, 2, 1, 1, 1]|ok
Coronel|ESTRIBADORA TJK 1|[2, 2, 1, 0, 0, 0, 0, 0, 0, 0]|[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Coronel|ESTRIBADORA TJK 2|[2, 2, 1, None, 0, 0, 0, 0, 0, 0]|[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]|ok
Coronel|Linea Corte Coronel|[10, 10, 6, 3, 3, 1, 1, 1, 1, 1]|[10, 10, 6, 3, 3, 1, 1, 1, 1, 1]|ok
filas DIFF vs SQLite: 0 / 30
claves Excel conservadas (maquinas sin fila SQLite): 0 []
maquinas del motor (diametros) sin fila en hebras -> default 1: []
claves hebras_x_maquina  viejo: 92  nuevo: 151
valores <1 en nuevo: []

== B) Cambio de duracion estimada (estimar_duracion_min, viejo vs nuevo) ==
SUC|MAQUINA|IdForma|diam|kg|dur_VIEJO_min|dur_NUEVO_min|hebras_nuevo
Coronel|Dobladora 2|3|10|500|51.5|6.4|8
Coronel|Dobladora 2|3|12|500|51.5|8.6|6
Coronel|Dobladora 2|3|16|500|51.5|17.2|3
Coronel|Linea Corte Coronel|1|12|500|28.5|5.0|6
Cerrillos|LINEA DE CORTE|1|16|500|8.7|5.0|15
Cerrillos|Dobladora Tecmor S40 1|2|18|500|30.2|15.1|2
Calama|Carro de Corte|1|12|500|14.5|7.3|2
Cerrillos|FORMULA 12|164|10|500|10.0|10.0|2
```

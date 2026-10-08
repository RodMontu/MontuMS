cd /c/Users/OptiFierro/Desktop/optifierro_int/backend
for t in test_f4_operadores test_adelanto_automatico test_cajita_viaje test_b16_capacidad test_b42v2_etiquetas test_motor_averias_cubigest_fusion test_f8_ribete_adelanto test_cuadro_resumen test_estado_maquinas; do
  R=$(timeout 100 python -m unittest $t 2>&1 | grep -E '^(Ran|OK|FAILED)' | tr '\n' ' ')
  echo "$t: $R"
done
echo FIN

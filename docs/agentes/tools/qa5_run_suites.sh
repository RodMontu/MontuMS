cd /c/Users/OptiFierro/Desktop/optifierro_int/backend
for t in test_f4_operadores test_f8_ribete_adelanto test_cuadro_resumen test_version_endpoint test_cajita_viaje test_b16_capacidad test_estado_maquinas test_universo_fechas test_adelanto_automatico test_b42v2_etiquetas test_gantt_etapa_gris test_migracion_scraper_optisteel test_motor_averias_cubigest_fusion test_sync_unificado test_averias_cubigest test_b44b_capacidad_real test_decodificar_material; do
  R=$(timeout 90 python -m unittest $t 2>&1 | tail -3 | tr '\n' ' ')
  echo "$t: $R" | cut -c1-150
done
echo FIN

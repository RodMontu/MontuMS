"""
F4 (QA SPP 05-10-2026): operador vs ayudante por cargo de Geovictoria; maquina detenida sin operador.
Sin red ni DB real: mockea httpx y estado_maquinas.
Ejecutar: python -m unittest test_f4_operadores -v
"""
import os
import sys
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cargos
from routers import programacion

HOY = datetime.now().strftime("%Y-%m-%d")

# Roster real de Coronel del 05-10-2026 (Geovictoria, contenedor geovictoria_api)
ROSTER_CORONEL = [
    {"nombre": "Cristian Aaron Escalona Matamoro", "cargo": "Mecanico Junior", "turno_inferido": "dia"},
    {"nombre": "Cristian Daniel Urra Astete", "cargo": "Ayte del Operador", "turno_inferido": "dia"},
    {"nombre": "Damian Alonso Neira Vitallos", "cargo": "Operador Junior Practica", "turno_inferido": "dia"},
    {"nombre": "Dilan Alexander Diaz Montecinos", "cargo": "Ayte del Operador", "turno_inferido": "dia"},
    {"nombre": "Enzo Isaac Lara Peña", "cargo": "Operador Junior", "turno_inferido": "dia"},
    {"nombre": "Kurt Carlos Franklin Gallegos Lara", "cargo": "Operador Junior", "turno_inferido": "dia"},
    {"nombre": "Matías Ignacio Urra Astete", "cargo": "Ayte del Operador", "turno_inferido": "dia"},
    {"nombre": "Rafael Alonso Neira Sanhueza", "cargo": "Operador Senior", "turno_inferido": "dia"},
]
for _p in ROSTER_CORONEL:
    _p["fecha_referencia"] = HOY


class TestClasificacionPorCargo(unittest.TestCase):
    def test_operadores(self):
        for c in ("Operador Senior", "Operador Junior", "Operador Junior Practica", "Operador", "OPERADOR SENIOR"):
            self.assertTrue(cargos.es_operador(c), c)
            self.assertFalse(cargos.es_ayudante(c), c)

    def test_ayudantes_no_son_operadores(self):
        for c in ("Ayte del Operador", "Ayudante de Operador", "ayudante de operador", "AYTE DEL OPERADOR"):
            self.assertTrue(cargos.es_ayudante(c), c)
            self.assertFalse(cargos.es_operador(c), c)

    def test_otros_cargos_no_son_operadores(self):
        for c in ("Mecanico Junior", "Supervisor", "", None, "0:00:00"):
            self.assertFalse(cargos.es_operador(c), c)

    def test_jornada_usa_el_mismo_criterio(self):
        from routers import jornada
        self.assertTrue(jornada._es_ayudante("Ayte del Operador"))
        self.assertFalse(jornada._es_operador("Ayte del Operador"))
        self.assertTrue(jornada._es_operador("Operador Senior"))


class TestFiltroPresentes(unittest.TestCase):
    def test_coronel_real_deja_4_operadores(self):
        r = cargos.filtrar_presentes_por_cargo(ROSTER_CORONEL, "t")
        self.assertEqual(
            sorted(p["nombre"].split()[0] for p in r),
            ["Damian", "Enzo", "Kurt", "Rafael"],
        )

    def test_sin_cargo_utilizable_no_filtra(self):
        sin_cargo = [{"nombre": "A B C D", "cargo": ""}, {"nombre": "E F G H", "cargo": "0:00:00"}]
        self.assertEqual(cargos.filtrar_presentes_por_cargo(sin_cargo, "t"), sin_cargo)

    def test_lista_vacia(self):
        self.assertEqual(cargos.filtrar_presentes_por_cargo([], "t"), [])


class _Resp:
    status_code = 200

    def __init__(self, data):
        self._d = data

    def json(self):
        return self._d


class TestOperadoresDisponibles(unittest.TestCase):
    def test_ayudantes_con_autorizaciones_en_matriz_no_entran_al_pool(self):
        habilitados = ["dneira", "elara", "kgallegos", "rneira", "murra", "ddiaz", "curra"]
        conocimiento = SimpleNamespace(operadores_x_maquina={("Coronel", "Dobladora 3"): habilitados})
        with mock.patch.object(programacion.httpx, "get", return_value=_Resp(ROSTER_CORONEL)):
            pool = programacion._obtener_operadores_disponibles(14, conocimiento, "dia")
        self.assertEqual(sorted(pool), ["dneira", "elara", "kgallegos", "rneira"])
        for ayudante in ("murra", "ddiaz", "curra"):
            self.assertNotIn(ayudante, pool)

    def test_gv_caido_mantiene_fallback_anterior(self):
        conocimiento = SimpleNamespace(operadores_x_maquina={("Coronel", "Dobladora 3"): ["elara", "murra"]})
        with mock.patch.object(programacion.httpx, "get", side_effect=RuntimeError("caido")):
            pool = programacion._obtener_operadores_disponibles(14, conocimiento, "dia")
        self.assertEqual(sorted(pool), ["elara", "murra"])  # fallback documentado: sin datos de cargo


class TestMaquinaDetenidaSinOperador(unittest.TestCase):
    def _recursos(self):
        return [
            {"nombre": "Linea Corte Coronel", "operador": "Hector Manuel Acuña Sanhueza",
             "operador_noche": "Sin datos", "estado_maquina": "Operativa"},
            {"nombre": "Dobladora 2", "operador": "Enzo Isaac Lara Peña",
             "operador_noche": "Sin datos", "estado_maquina": "Operativa"},
        ]

    def test_detenida_pierde_operador_y_las_demas_no(self):
        estados = {
            "LINEA CORTE CORONEL": {"estado_motor": "detenida"},
            "DOBLADORA 2": {"estado_motor": "operativa"},
        }
        with mock.patch("estado_maquinas.obtener_estado_efectivo_maquinas", return_value=estados):
            out = programacion._quitar_operador_de_maquinas_detenidas(self._recursos(), 14)
        self.assertEqual(out[0]["operador"], "Sin Operador Asignado")
        self.assertEqual(out[1]["operador"], "Enzo Isaac Lara Peña")

    def test_semioperativa_conserva_operador(self):
        estados = {"LINEA CORTE CORONEL": {"estado_motor": "semi-operativa"}}
        with mock.patch("estado_maquinas.obtener_estado_efectivo_maquinas", return_value=estados):
            out = programacion._quitar_operador_de_maquinas_detenidas(self._recursos(), 14)
        self.assertEqual(out[0]["operador"], "Hector Manuel Acuña Sanhueza")

    def test_error_no_rompe(self):
        with mock.patch("estado_maquinas.obtener_estado_efectivo_maquinas", side_effect=RuntimeError("x")):
            out = programacion._quitar_operador_de_maquinas_detenidas(self._recursos(), 14)
        self.assertEqual(len(out), 2)


class TestGestorOperadoresSinAyudantes(unittest.TestCase):
    def setUp(self):
        from routers import operadores
        self.op = operadores
        self.op._CACHE_AYUDANTES.clear()

    def test_oculta_ayudantes_presentes_por_nombre_completo(self):
        filas = [
            {"Operador": "murra", "Nombre": "Matías Ignacio Urra Astete"},   # Ayte -> se oculta
            {"Operador": "curra", "Nombre": "Cristofer Andrés Urra Salgado"},  # otra persona (mismo username): NO se oculta por nombre
            {"Operador": "elara", "Nombre": "Enzo Isaac Lara Peña"},           # Operador Junior
        ]
        with mock.patch.object(self.op.httpx, "get", return_value=_Resp(ROSTER_CORONEL)):
            out = self.op._excluir_ayudantes_presentes(filas, 14)
        self.assertEqual([f["Operador"] for f in out], ["curra", "elara"])

    def test_sin_geovictoria_no_oculta_a_nadie(self):
        filas = [{"Operador": "murra", "Nombre": "Matías Ignacio Urra Astete"}]
        with mock.patch.object(self.op.httpx, "get", side_effect=RuntimeError("caido")):
            out = self.op._excluir_ayudantes_presentes(filas, 14)
        self.assertEqual(out, filas)


class TestNombreOperadorPorSucursal(unittest.TestCase):
    """El mismo username existe en varias plantas con personas distintas ('curra' Cerrillos vs Coronel)."""

    def _k(self):
        from motor_v2 import ConocimientoMotor
        k = ConocimientoMotor.__new__(ConocimientoMotor)
        k.nombre_por_username = {"curra": "Cristofer Andrés Urra Salgado"}  # el ultimo en cargarse (Cerrillos) gana
        k.nombre_por_sucursal_username = {
            ("Cerrillos", "curra"): "Cristofer Andrés Urra Salgado",
            ("Coronel", "curra"): "Cristian Daniel Urra Astete",
        }
        return k

    def test_resuelve_por_sucursal(self):
        k = self._k()
        self.assertEqual(k.resolver_nombre_operador("Coronel", "curra"), "Cristian Daniel Urra Astete")
        self.assertEqual(k.resolver_nombre_operador("Cerrillos", "curra"), "Cristofer Andrés Urra Salgado")

    def test_respaldo_y_vacios(self):
        k = self._k()
        self.assertEqual(k.resolver_nombre_operador("Calama", "curra"), "Cristofer Andrés Urra Salgado")  # respaldo legado
        self.assertEqual(k.resolver_nombre_operador("Coronel", "zzz"), "zzz")  # desconocido: devuelve el usuario
        self.assertEqual(k.resolver_nombre_operador("Coronel", ""), "")


class TestOperadorPresenteSinMaquinas(unittest.TestCase):
    def test_operador_senior_presente_se_reconoce_aunque_no_tenga_maquinas(self):
        from routers import operadores
        operadores._CACHE_AYUDANTES.clear()
        with mock.patch.object(operadores.httpx, "get", return_value=_Resp(ROSTER_CORONEL)):
            ayudantes, ops = operadores._nombres_presentes_por_cargo(14)
        self.assertIn("rafael alonso neira sanhueza", ops)
        self.assertIn("matias ignacio urra astete", ayudantes)
        self.assertNotIn("cristian aaron escalona matamoro", ops)  # Mecanico Junior
        self.assertNotIn("cristian aaron escalona matamoro", ayudantes)


if __name__ == "__main__":
    unittest.main(verbosity=2)

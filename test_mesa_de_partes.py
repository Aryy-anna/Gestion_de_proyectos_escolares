"""Pruebas del prototipo. Ejecutar:  python -m unittest -v"""
import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import mesa_de_partes as mp


def ejecutar(entradas, fecha="20261102"):
    """Corre main() con entradas simuladas y devuelve lo impreso."""
    salida = io.StringIO()
    with mock.patch("builtins.input", side_effect=entradas), \
            mock.patch.object(mp, "obtener_fecha_sistema", return_value=fecha), \
            redirect_stdout(salida):
        mp.main()
    return salida.getvalue()


REGISTRO_1 = ["1", "71234501", "Mateo Alonso Quispe Rojas", "987654321",
              "3", "3ro", "1", "1"]          # SECUNDARIA, ESTUDIANTE, CONSTANCIA
REGISTRO_2 = ["1", "45678912", "Ana Torres Vega", "912345678",
              "2", "6to", "2", "2"]          # PRIMARIA, EGRESADO, CERTIFICADO


class TestValidaciones(unittest.TestCase):
    def test_dni(self):
        self.assertTrue(mp.validar_dni("12345678"))
        self.assertFalse(mp.validar_dni("1234567"))
        self.assertFalse(mp.validar_dni("1234567a"))
        self.assertFalse(mp.validar_dni("1234567²"))

    def test_telefono(self):
        self.assertTrue(mp.validar_telefono("987654321"))
        self.assertFalse(mp.validar_telefono("887654321"))
        self.assertFalse(mp.validar_telefono("98765432"))

    def test_nombre(self):
        self.assertTrue(mp.validar_nombre("Ana Torres"))
        self.assertFalse(mp.validar_nombre("Ana"))

    def test_codigo_y_fecha(self):
        self.assertEqual(mp.generar_codigo(7), "SOL-007")
        self.assertEqual(mp.generar_codigo(42), "SOL-042")
        self.assertEqual(mp.generar_codigo(123), "SOL-123")
        self.assertEqual(mp.formatear_fecha("20261102"), "02/11/2026")
        self.assertEqual(len(mp.obtener_fecha_sistema()), 8)


class TestFlujoDeEstados(unittest.TestCase):
    def test_transiciones(self):
        self.assertTrue(mp.estado_permitido("RECIBIDO", "EN REVISION"))
        self.assertFalse(mp.estado_permitido("RECIBIDO", "ATENDIDO"))
        self.assertTrue(mp.estado_permitido("EN REVISION", "OBSERVADO"))
        self.assertTrue(mp.estado_permitido("EN REVISION", "ATENDIDO"))
        self.assertTrue(mp.estado_permitido("OBSERVADO", "EN REVISION"))
        self.assertFalse(mp.estado_permitido("OBSERVADO", "ATENDIDO"))
        self.assertFalse(mp.estado_permitido("ATENDIDO", "EN REVISION"))


class TestAcceso(unittest.TestCase):
    def test_acceso_correcto_en_segundo_intento(self):
        with mock.patch("builtins.input", side_effect=["XXX", "sec-02"]), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(mp.ingresar_acceso(["SEC-01", "SEC-02"]), 1)

    def test_acceso_denegado_tras_tres_intentos(self):
        with mock.patch("builtins.input", side_effect=["a", "b", "c"]), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(mp.ingresar_acceso(["SEC-01"]), -1)

    def test_programa_no_continua_sin_acceso(self):
        out = ejecutar(["a", "b", "c"])
        self.assertIn("Acceso denegado", out)
        self.assertNotIn("1. Registrar", out)


class TestProgramaCompleto(unittest.TestCase):
    def test_registro_usa_fecha_de_sistema_condicion_y_responsable(self):
        out = ejecutar(["SEC-01"] + REGISTRO_1 + ["5", "0"], "20261102")
        self.assertIn("Codigo asignado: SOL-001", out)
        self.assertIn("Fecha de registro: 02/11/2026", out)
        self.assertIn("Condicion: ESTUDIANTE", out)
        self.assertIn("Personal responsable: Mery Elizabeth Herrera Sanchez "
                      "(SEC-01)", out)
        self.assertNotIn("Seccion", out)

    def test_validacion_reintenta(self):
        out = ejecutar(["DIR-01", "1", "123", "71234501",
                        "Mateo", "Mateo Quispe", "812345678", "987654321",
                        "1", "Inicial 5", "2", "6", "0"])
        self.assertIn("DNI invalido", out)
        self.assertIn("Ingrese nombres y apellidos", out)
        self.assertIn("empezar con 9", out)
        self.assertIn("Codigo asignado: SOL-001", out)

    def test_cancelar_registro(self):
        out = ejecutar(["SEC-01", "1", "x", "0"])
        self.assertIn("Registro cancelado", out)
        self.assertNotIn("Codigo asignado", out)

    def test_busqueda_por_condicion(self):
        out = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                       ["2", "egresado", "0"])
        self.assertIn("Coincidencias encontradas: 1", out)
        self.assertIn("Ana Torres Vega", out)

    def test_ordenar_por_nombre_descendente_insercion(self):
        out = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                       ["3", "3", "2", "2", "0"])
        self.assertLess(out.rindex("Mateo Alonso"), out.rindex("Ana Torres"))

    def test_estado_observado_con_nota_y_vuelta_a_revision(self):
        out = ejecutar(["SEC-01"] + REGISTRO_1 + [
            "6", "SOL-001", "2",                    # RECIBIDO -> EN REVISION
            "6", "SOL-001", "3", "", "Falta copia del DNI",  # -> OBSERVADO
            "6", "SOL-001", "2",                    # OBSERVADO -> EN REVISION
            "0"])
        self.assertIn("Estado: EN REVISION", out)
        self.assertIn("Nota de observacion: Falta copia del DNI", out)
        self.assertIn("no puede quedar vacio", out)

    def test_no_se_puede_saltar_a_atendido_desde_recibido(self):
        out = ejecutar(["SEC-01"] + REGISTRO_1 + [
            "6", "SOL-001", "4", "0", "0"])
        self.assertIn("Cambio no permitido desde el estado RECIBIDO", out)

    def test_aprobar_y_rechazar_y_reportes(self):
        out = ejecutar(["SEC-02"] + REGISTRO_1 + REGISTRO_2 + [
            "6", "SOL-001", "2",
            "6", "SOL-001", "4", "1",               # ATENDIDO - APROBADO
            "6", "SOL-002", "2",
            "6", "SOL-002", "4", "2", "Documento ilegible",  # RECHAZADO
            "6", "SOL-002",                         # ya atendida: no pide nada mas
            "4", "7", "8", "0"])
        self.assertIn("Estado: ATENDIDO - APROBADO", out)
        self.assertIn("Estado: ATENDIDO - RECHAZADO", out)
        self.assertIn("Nota de observacion: Documento ilegible", out)
        self.assertIn("ya fue atendida", out)
        self.assertIn("Atendidos: 1 aprobados y 1 rechazados", out)
        self.assertIn("CONSTANCIA DE ESTUDIOS | 1 | 0 | 1 | 0", out)
        self.assertIn("CERTIFICADO DE ESTUDIOS | 1 | 0 | 0 | 1", out)
        self.assertIn("TOTAL | 2 | 0 | 1 | 1", out)
        self.assertIn("02/11/2026 | 2 | 100.0% | SOL-001, SOL-002", out)
        self.assertIn("TOTAL DE INGRESOS: 2", out)

    def test_codigo_inexistente(self):
        out = ejecutar(["SEC-01"] + REGISTRO_1 + ["6", "SOL-999", "0"])
        self.assertIn("No existe una solicitud con ese codigo", out)

    def test_indice_en_dos_fechas(self):
        fechas = ["20261102", "20261102", "20261103"]
        entradas = iter(["SEC-01"] + REGISTRO_1 + REGISTRO_2 + REGISTRO_2 +
                        ["8", "0"])
        salida = io.StringIO()
        with mock.patch("builtins.input", side_effect=lambda _="": next(entradas)), \
                mock.patch.object(mp, "obtener_fecha_sistema",
                                  side_effect=fechas), \
                redirect_stdout(salida):
            mp.main()
        out = salida.getvalue()
        self.assertIn("02/11/2026 | 2 | 66.7% | SOL-001, SOL-002", out)
        self.assertIn("03/11/2026 | 1 | 33.3% | SOL-003", out)

    def test_sin_datos(self):
        out = ejecutar(["SEC-01", "2", "3", "5", "6", "8", "0"])
        self.assertEqual(out.count("No hay solicitudes"), 5)


if __name__ == "__main__":
    unittest.main()

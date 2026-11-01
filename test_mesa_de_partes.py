"""Pruebas automaticas de las funciones puras del prototipo.
Ejecutar:  python -m unittest -v test_mesa_de_partes
"""
import os
import tempfile
import unittest

import mesa_de_partes as mp

CAT_ESTADOS = ["RECIBIDO", "EN REVISION", "OBSERVADO", "APROBADO",
               "RECHAZADO", "ATENDIDO"]
PERMITIDO = [[0, 1, 0, 0, 0, 0],
             [0, 0, 1, 1, 1, 0],
             [0, 1, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]


class TestValidaciones(unittest.TestCase):
    def test_codigo_generado(self):
        self.assertEqual(mp.generar_codigo(1), "SOL-001")
        self.assertEqual(mp.generar_codigo(25), "SOL-025")
        self.assertEqual(mp.generar_codigo(200), "SOL-200")

    def test_dni(self):
        self.assertTrue(mp.validar_dni("71234501"))
        self.assertFalse(mp.validar_dni("1234567"))      # 7 digitos
        self.assertFalse(mp.validar_dni("7123450A"))     # letra
        self.assertFalse(mp.validar_dni("7123450²"))  # simbolo

    def test_telefono(self):
        self.assertTrue(mp.validar_telefono("987654321"))
        self.assertFalse(mp.validar_telefono("887654321"))  # no empieza con 9
        self.assertFalse(mp.validar_telefono("98765432"))   # 8 digitos

    def test_nombre(self):
        self.assertTrue(mp.validar_nombre("Mateo Quispe"))
        self.assertFalse(mp.validar_nombre("Mateo"))
        self.assertFalse(mp.validar_nombre("    "))

    def test_acceso_por_codigo(self):
        codigos = ["SEC-01", "SEC-02"]
        self.assertEqual(mp.buscar_personal("sec-02", codigos), 1)
        self.assertEqual(mp.buscar_personal("XYZ", codigos), -1)

    def test_fecha_sistema(self):
        f = mp.fecha_del_sistema()
        self.assertRegex(f, r"^\d{4}-\d{2}-\d{2}$")


class TestBusquedaOrdenYEstados(unittest.TestCase):
    def test_busqueda_por_codigo(self):
        codigos = ["SOL-001", "SOL-002", "SOL-003"]
        self.assertEqual(mp.buscar_por_codigo(codigos, 3, "sol-003"), (2, 3))
        self.assertEqual(mp.buscar_por_codigo(codigos, 3, "SOL-999"), (-1, 3))

    def test_orden_insercion(self):
        codigos = ["SOL-003", "SOL-001", "SOL-002"]
        orden = [0] * 3
        mp.ordenar_insercion(orden, codigos, 3, True)
        self.assertEqual(orden, [1, 2, 0])
        mp.ordenar_insercion(orden, codigos, 3, False)
        self.assertEqual(orden, [0, 2, 1])

    def test_flujo_de_estados(self):
        f = lambda e: mp.estados_siguientes(e, CAT_ESTADOS, PERMITIDO)
        self.assertEqual(f("RECIBIDO"), ["EN REVISION"])
        self.assertEqual(f("EN REVISION"),
                         ["OBSERVADO", "APROBADO", "RECHAZADO"])
        self.assertEqual(f("OBSERVADO"), ["EN REVISION", "RECHAZADO"])
        self.assertEqual(f("APROBADO"), ["ATENDIDO"])
        self.assertEqual(f("RECHAZADO"), [])
        self.assertEqual(f("ATENDIDO"), [])


class TestArchivo(unittest.TestCase):
    def test_guardar_y_cargar(self):
        original = mp.ARCHIVO
        with tempfile.TemporaryDirectory() as carpeta:
            mp.ARCHIVO = os.path.join(carpeta, "prueba.csv")
            try:
                cols = [[""] * 5 for _ in range(12)]
                for c in range(12):
                    cols[c][0] = "dato" + str(c)
                cols[11][0] = "Falta; copia\ndel DNI"   # separador y salto
                mp.guardar_archivo(cols, 1)

                cols2 = [[""] * 5 for _ in range(12)]
                self.assertEqual(mp.cargar_archivo(cols2), 1)
                self.assertEqual(cols2[0][0], "dato0")
                self.assertEqual(cols2[11][0], "Falta, copia del DNI")
            finally:
                mp.ARCHIVO = original

    def test_archivo_inexistente(self):
        original = mp.ARCHIVO
        mp.ARCHIVO = "no_existe_xyz.csv"
        try:
            self.assertEqual(mp.cargar_archivo([[""] * 5]), 0)
        finally:
            mp.ARCHIVO = original


if __name__ == "__main__":
    unittest.main()

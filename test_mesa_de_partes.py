"""Pruebas del prototipo. Ejecutar:  python -m unittest -v"""
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import IE_MARIA_INMACULADA as mp


def ejecutar(entradas, fecha="20261104", hora="15:59", carpeta=None):
    """Corre main() con entradas simuladas y devuelve (salida, carpeta).
    Los .txt se escriben en una carpeta temporal."""
    if carpeta is None:
        tmp = tempfile.TemporaryDirectory()
        carpeta = tmp.name
        ejecutar.tmps.append(tmp)
    salida = io.StringIO()
    with mock.patch("builtins.input", side_effect=entradas), \
            mock.patch.object(mp, "obtener_fecha_sistema", return_value=fecha), \
            mock.patch.object(mp, "obtener_hora_sistema", return_value=hora), \
            mock.patch.object(mp, "limpiar_pantalla"), \
            mock.patch.object(mp, "esperar_tecla"), \
            mock.patch("shutil.get_terminal_size",
                       return_value=os.terminal_size((200, 30))), \
            mock.patch.object(mp, "ARCHIVO_TRAMITE",
                              os.path.join(carpeta, "Tramite.txt")), \
            mock.patch.object(mp, "ARCHIVO_SEGUIMIENTO",
                              os.path.join(carpeta, "Seguimiento.txt")), \
            redirect_stdout(salida):
        mp.main()
    return salida.getvalue(), carpeta


ejecutar.tmps = []


def leer(carpeta, nombre):
    with open(os.path.join(carpeta, nombre), encoding="utf-8") as f:
        return f.read().splitlines()


# Orden: opcion, condicion, dni, apellidos, nombres, celular, nivel, grado,
#        tramite, folios
REGISTRO_1 = ["1", "1", "71234501", "Quispe Rojas", "Mateo Alonso",
              "987654321", "3", "3", "1", "6", "S"]   # ESTUDIANTE, SECUNDARIA
REGISTRO_2 = ["1", "2", "45678912", "Torres Vega", "Ana",
              "912345678", "19", "2", "3", "S"]   # EGRESADO (sin nivel; pide edad)


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
        self.assertTrue(mp.validar_nombre("Castillo Zumaran"))
        self.assertTrue(mp.validar_nombre("Ana"))
        self.assertFalse(mp.validar_nombre("A"))
        self.assertFalse(mp.validar_nombre("Ana2"))
        self.assertFalse(mp.validar_nombre("Ana|Luz"))

    def test_codigo_y_fecha(self):
        self.assertEqual(mp.generar_codigo(7), "SOL-007")
        self.assertEqual(mp.generar_codigo(42), "SOL-042")
        self.assertEqual(mp.generar_codigo(123), "SOL-123")
        self.assertEqual(mp.numero_de_codigo("SOL-007"), 7)
        self.assertEqual(mp.formatear_fecha("20261104"), "04/11/2026")
        self.assertEqual(len(mp.obtener_fecha_sistema()), 8)
        self.assertEqual(len(mp.obtener_hora_sistema()), 5)

    def test_fecha_de_archivo(self):
        self.assertEqual(mp.fecha_a_txt("20261104"), "4-11-26")
        self.assertEqual(mp.fecha_a_txt("20260305"), "5-3-26")
        self.assertEqual(mp.txt_a_fecha("4-11-26"), "20261104")
        self.assertEqual(mp.txt_a_fecha("5-3-26"), "20260305")
        self.assertEqual(mp.txt_a_fecha("basura"), "")


class TestFlujoDeEstados(unittest.TestCase):
    def test_transiciones(self):
        p = mp.estado_permitido
        self.assertTrue(p("Registrado", "En revision"))
        self.assertFalse(p("Registrado", "Observado"))
        self.assertFalse(p("Registrado", "Aprobado"))
        self.assertTrue(p("En revision", "Observado"))
        self.assertFalse(p("En revision", "Aprobado"))
        self.assertFalse(p("En revision", "Rechazado"))
        self.assertTrue(p("Observado", "Aprobado"))
        self.assertTrue(p("Observado", "Rechazado"))
        self.assertFalse(p("Observado", "En revision"))
        self.assertFalse(p("Aprobado", "Observado"))
        self.assertFalse(p("Rechazado", "Aprobado"))

    def test_solo_el_director_asigna_aprobado_y_rechazado(self):
        self.assertFalse(mp.puede_asignar("Aprobado", False))
        self.assertFalse(mp.puede_asignar("Rechazado", False))
        self.assertTrue(mp.puede_asignar("En revision", False))
        self.assertTrue(mp.puede_asignar("Observado", False))
        self.assertTrue(mp.puede_asignar("Aprobado", True))
        self.assertTrue(mp.puede_asignar("Rechazado", True))


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
        out, _ = ejecutar(["a", "b", "c"])
        self.assertIn("Acceso denegado", out)
        self.assertNotIn("1. Registrar", out)


class TestRegistro(unittest.TestCase):
    def test_condicion_se_pregunta_antes_que_nivel_y_grado(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        # (los textos de input() no salen en pantalla al simularlos;
        # se comparan los encabezados de cada lista)
        self.assertLess(out.index("CONDICION"), out.index("NIVELES EDUCATIVOS"))
        self.assertLess(out.index("CONDICION"), out.index("TIPOS DE TRAMITE"))

    def test_registro_usa_fecha_hora_de_sistema_y_responsable(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + ["4", "0"])
        self.assertIn("Codigo asignado: SOL-001", out)
        self.assertIn("Fecha y hora de registro: 04/11/2026 15:59", out)
        self.assertIn("Estado inicial: Registrado", out)

    def test_tramite_txt_con_el_formato_pedido(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 + ["0"])
        self.assertEqual(leer(carpeta, "Tramite.txt"), [
            "SOL-001|4-11-26|15:59|1|71234501|Quispe Rojas|Mateo Alonso|"
            "987654321|ESTUDIANTE|SECUNDARIA|3|CONSTANCIA DE ESTUDIOS|6|SEC-01",
            "SOL-002|4-11-26|15:59|1|45678912|Torres Vega|Ana|"
            "912345678|EGRESADO|-|19|CERTIFICADO DE ESTUDIOS|3|SEC-01",
        ])

    def test_seguimiento_txt_al_registrar(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        self.assertEqual(leer(carpeta, "Seguimiento.txt"), [
            "1|Registrado|4-11-26|15:59|Solicitud registrada|SEC-01"])

    def test_el_separador_no_rompe_el_archivo(self):
        reg = list(REGISTRO_1)
        reg[3] = "Quispe|Rojas"
        # el '|' se rechaza en la validacion y se pide de nuevo
        out, carpeta = ejecutar(["SEC-01"] + reg[:4] + ["Quispe Rojas"]
                                + reg[4:] + ["0"])
        self.assertIn("Ingrese los apellidos", out)
        self.assertEqual(len(leer(carpeta, "Tramite.txt")[0].split("|")), 14)

    def test_validacion_reintenta(self):
        out, _ = ejecutar(["DIR-01", "1", "9", "1", "123", "71234501",
                           "R2", "Rojas", "M1", "Mateo", "812345678",
                           "987654321", "1", "Inicial 5", "9", "4", "2", "0", "2", "S", "0"])
        self.assertIn("Ingrese 1, 2 o X", out)
        self.assertIn("DNI invalido", out)
        self.assertIn("Ingrese los apellidos", out)
        self.assertIn("Ingrese los nombres", out)
        self.assertIn("empezar con 9", out)
        self.assertIn("Ingrese un numero entero", out)
        self.assertIn("entre 3 y 5", out)
        self.assertIn("al menos 1 folio", out)
        self.assertIn("Codigo asignado: SOL-001", out)

    def test_cancelar_registro(self):
        out, carpeta = ejecutar(["SEC-01", "1", "x", "0"])
        self.assertIn("Registro cancelado", out)
        self.assertNotIn("Codigo asignado", out)
        self.assertFalse(os.path.exists(os.path.join(carpeta, "Tramite.txt")))

    def test_cancelar_en_dni(self):
        out, _ = ejecutar(["SEC-01", "1", "1", "x", "0"])
        self.assertIn("Registro cancelado", out)


class TestTramitesYGradoPorCondicion(unittest.TestCase):
    def test_menu_principal_sin_opcion_8_ni_reporte_repetido(self):
        out, _ = ejecutar(["SEC-01", "0"])
        self.assertIn("4. Reporte de documentos", out)
        self.assertIn("6. Actualizar estado de una solicitud", out)
        self.assertIn("5. Lista de tramites\n", out)
        self.assertNotIn("7.", out)
        self.assertNotIn("abrir expediente", out)
        self.assertNotIn("8.", out)
        self.assertNotIn("Reporte por tramite", out)

    def test_egresado_no_ve_justificacion_ni_matricula(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_2 + ["0"])
        lista = out[out.index("TIPOS DE TRAMITE"):out.index("[OK]")]
        self.assertIn("1. CONSTANCIA DE ESTUDIOS", lista)
        self.assertIn("2. CERTIFICADO DE ESTUDIOS", lista)
        self.assertIn("3. ACTUALIZACION DE DATOS", lista)
        self.assertIn("4. OTROS", lista)
        self.assertNotIn("JUSTIFICACION", lista)
        self.assertNotIn("MATRICULA", lista)

    def test_estudiante_ve_todos_los_tramites(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        lista = out[out.index("TIPOS DE TRAMITE"):out.index("[OK]")]
        self.assertIn("4. JUSTIFICACION DE INASISTENCIA", lista)
        self.assertIn("6. OTROS", lista)

    def test_egresado_guarda_el_numero_del_catalogo(self):
        reg = list(REGISTRO_2)
        reg[7] = "3"      # 3ro de la lista del egresado = ACTUALIZACION DE DATOS
        out, carpeta = ejecutar(["SEC-01"] + reg + ["5", "SOL-001", "0", "0"])
        self.assertIn("ACTUALIZACION DE DATOS", out)
        self.assertEqual(leer(carpeta, "Tramite.txt")[0].split("|")[11],
                         "ACTUALIZACION DE DATOS")

    def test_estudiante_solo_indica_su_grado(self):
        # secundaria: 6 no vale (1-5), luego 4
        reg = list(REGISTRO_1)
        reg[7] = "6"
        out, _ = ejecutar(["SEC-01"] + reg[:8] + ["4"] + reg[8:]
                          + ["2", "1", "SOL-001", "0"])
        self.assertIn("entre 1 y 5", out)
        fila = [l for l in out.splitlines() if l.startswith("| SOL-001")][0]
        self.assertIn("| 4 ", fila)

    def test_egresado_no_pregunta_nivel_y_va_a_la_edad(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_2 + ["0"])
        self.assertNotIn("NIVELES EDUCATIVOS", out)

    def test_estudiante_si_pregunta_nivel(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        self.assertIn("NIVELES EDUCATIVOS", out)

    def test_busqueda_y_orden_sin_conteos_ni_metodo(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                          ["2", "3", "ana", "3", "1", "1", "0"])
        self.assertIn("Coincidencias encontradas: 1", out)
        for texto in ("Comparaciones", "Intercambios", "burbuja",
                      "insercion", "Ordenamiento aplicado", "metodo"):
            self.assertNotIn(texto, out)

    def test_egresado_puede_poner_edad(self):
        reg = list(REGISTRO_2)
        reg[6] = "25"
        out, _ = ejecutar(["SEC-01"] + reg + ["2", "1", "SOL-001", "0"])
        fila = [l for l in out.splitlines() if l.startswith("| SOL-001")][0]
        self.assertIn("| 25 ", fila)
        self.assertIn("| EGRESADO  | -     | 25 ", fila)


class TestPersistencia(unittest.TestCase):
    def test_los_datos_se_recuperan_al_abrir_de_nuevo(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + [
            "6", "1", "1", "Revision inicial", "0"])
        out, _ = ejecutar(["SEC-01", "5", "SOL-001", "0", "0"],
                          carpeta=carpeta)
        self.assertIn("Se cargaron 1 solicitud(es)", out)
        self.assertIn("Remitente: Quispe Rojas, Mateo Alonso", out)
        self.assertIn("Estado: En revision", out)

    def test_la_numeracion_continua_tras_reabrir(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        out, carpeta = ejecutar(["SEC-01"] + REGISTRO_2 + ["0"],
                                carpeta=carpeta)
        self.assertIn("Codigo asignado: SOL-002", out)
        self.assertEqual(len(leer(carpeta, "Tramite.txt")), 2)


class TestBusquedaYOrden(unittest.TestCase):
    def test_busqueda_por_condicion(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                          ["2", "5", "egresado", "0"])
        self.assertIn("Coincidencias encontradas: 1", out)
        self.assertIn("Torres Vega, Ana", out)

    def test_busqueda_por_apellido_o_nombre(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                          ["2", "3", "quispe", "2", "3", "ana", "0"])
        self.assertEqual(out.count("Coincidencias encontradas: 1"), 2)

    def test_ordenar_por_nombre_descendente_insercion(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                          ["3", "3", "2", "0"])
        # descendente: Torres (T) va antes que Quispe (Q)
        self.assertLess(out.rindex("Torres Vega"), out.rindex("Quispe Rojas"))

    def test_ordenar_muestra_una_tabla_con_una_fila_por_solicitud(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                          ["3", "1", "1", "0"])
        fin = out[out.index("ORDENAMIENTO DE SOLICITUDES"):]
        filas = [l for l in fin.splitlines() if l.startswith("| SOL-")]
        self.assertEqual(len(filas), 2)
        self.assertIn("Quispe Rojas", filas[0])
        self.assertIn("Torres Vega", filas[1])
        encabezado = [l for l in fin.splitlines() if "| CODIGO" in l]
        self.assertEqual(len(encabezado), 1)
        # todas las lineas de la tabla miden lo mismo (columnas alineadas)
        tabla = [l for l in fin.splitlines() if l[:1] in ("|", "+")]
        self.assertEqual(len(set(len(l) for l in tabla)), 1)
        self.assertNotIn("Codigo de solicitud:", fin)


class TestEstadosYSeguimiento(unittest.TestCase):
    def test_flujo_completo_registrado_revision_observado_aprobado(self):
        out, carpeta = ejecutar(["DIR-01"] + REGISTRO_1 + [
            "6", "1", "1", "Documentos completos",      # -> En revision
            "6", "SOL-001", "1", "",                    # motivo vacio
            "Falta copia del DNI",                      # -> Observado
            "6", "1", "1", "Presento el DNI", "S",      # 1 = Aprobado
            "0"])
        self.assertIn("Estado: En revision", out)
        self.assertIn("Estado: Observado", out)
        self.assertIn("Motivo del estado: Falta copia del DNI", out)
        self.assertIn("no puede quedar vacio", out)
        self.assertIn("Estado: Aprobado", out)
        self.assertEqual(leer(carpeta, "Seguimiento.txt"), [
            "1|Registrado|4-11-26|15:59|Solicitud registrada|DIR-01",
            "1|En revision|4-11-26|15:59|Documentos completos|DIR-01",
            "1|Observado|4-11-26|15:59|Falta copia del DNI|DIR-01",
            "1|Aprobado|4-11-26|15:59|Presento el DNI|DIR-01",
        ])

    def test_registrado_solo_ofrece_en_revision(self):
        out, _ = ejecutar(["DIR-01"] + REGISTRO_1 + [
            "6", "1", "0", "0"])
        self.assertIn("ESTADOS DISPONIBLES\n1. En revision\n", out)
        self.assertNotIn("2. ", out[out.index("ESTADOS DISPONIBLES"):
                                    out.index("ESTADOS DISPONIBLES") + 60])

    def test_no_se_puede_saltar_a_aprobado_desde_registrado(self):
        out, carpeta = ejecutar(["DIR-01"] + REGISTRO_1 + [
            "6", "SOL-001", "2", "0", "0"])
        self.assertIn("Opcion no valida", out)
        self.assertEqual(len(leer(carpeta, "Seguimiento.txt")), 1)

    def test_secretaria_edita_en_revision_y_observado_pero_no_el_resto(self):
        out, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + [
            "6", "1", "1", "Documentos completos",   # Registrado -> En revision
            "6", "1", "1", "Falta el DNI",           # En revision -> Observado
            "6", "1", "0"])
        self.assertIn("Estado: En revision", out)
        self.assertIn("Estado: Observado", out)
        self.assertIn("Solo el director puede aprobar o rechazar", out)
        self.assertNotIn("1. Aprobado", out)
        self.assertNotIn("2. Rechazado", out)
        lineas = leer(carpeta, "Seguimiento.txt")
        self.assertEqual(len(lineas), 3)
        self.assertTrue(lineas[2].endswith("|Falta el DNI|SEC-01"))

    def test_director_ve_aprobado_y_rechazado_tras_observado(self):
        out, _ = ejecutar(["DIR-01"] + REGISTRO_1 + [
            "6", "1", "1", "Documentos completos",
            "6", "1", "1", "Falta el DNI",
            "6", "1", "0", "0"])
        self.assertIn("1. Aprobado\n2. Rechazado", out)

    def test_estado_final_no_se_modifica(self):
        out, carpeta = ejecutar(["DIR-01"] + REGISTRO_1 + [
            "6", "1", "1", "Documentos completos",
            "6", "1", "1", "Falta el DNI",
            "6", "1", "2", "Documento ilegible", "S",       # 2 = Rechazado
            "6", "1", "0"])
        self.assertIn("ya esta en un estado final (Rechazado)", out)
        self.assertEqual(len(leer(carpeta, "Seguimiento.txt")), 4)

    def test_cancelar_cambio_no_escribe(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + [
            "6", "SOL-001", "0", "0"])
        self.assertEqual(len(leer(carpeta, "Seguimiento.txt")), 1)

    def test_reportes(self):
        out, _ = ejecutar(["DIR-01"] + REGISTRO_1 + REGISTRO_2 + [
            "6", "SOL-001", "1", "revision",
            "6", "SOL-001", "1", "observado",
            "6", "SOL-001", "1", "todo en orden", "S",      # Aprobado
            "6", "SOL-002", "1", "revision",
            "6", "SOL-002", "1", "observado",
            "6", "SOL-002", "2", "Documento ilegible", "S",  # Rechazado
            "4", "0"])
        self.assertIn("Estado: Rechazado", out)
        self.assertIn("Motivo del estado: Documento ilegible", out)
        self.assertIn("===== REPORTE DE DOCUMENTOS =====", out)
        self.assertNotIn("REPORTE POR TRAMITE", out)
        self.assertIn("TRAMITE | REGISTRADO | EN REVISION | OBSERVADO | "
                      "APROBADO | RECHAZADO | TOTAL", out)
        self.assertIn("CONSTANCIA DE ESTUDIOS | 0 | 0 | 0 | 1 | 0 | 1", out)
        self.assertIn("CERTIFICADO DE ESTUDIOS | 0 | 0 | 0 | 0 | 1 | 1", out)
        self.assertIn("TOTAL GENERAL: 2", out)

    def test_codigo_inexistente(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + ["6", "SOL-999", "0"])
        self.assertIn("No existe una solicitud con ese codigo", out)


class TestListaYExpediente(unittest.TestCase):
    def test_lista_y_apertura_de_expediente(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 + [
            "6", "1", "1", "Revision inicial",
            "5", "SOL-001", "9", "0", "0"])
        self.assertIn("===== LISTA DE TRAMITES / EXPEDIENTES =====", out)
        self.assertIn("SOL-002 | 04/11/2026 | CERTIFICADO DE ESTUDIOS | "
                      "Torres Vega, Ana | Registrado", out)
        self.assertIn("===== EXPEDIENTE SOL-001 =====", out)
        self.assertIn("Remitente: Quispe Rojas, Mateo Alonso", out)
        self.assertIn("DNI: 71234501", out)
        self.assertIn("Estado: En revision", out)
        self.assertIn("04/11/2026 15:59 | En revision | Revision inicial"
                      " | SEC-01", out)
        self.assertIn("No existe un expediente", out)

    def test_sin_datos(self):
        out, _ = ejecutar(["SEC-01", "2", "3", "5", "6", "0"])
        self.assertEqual(out.count("No hay solicitudes"), 4)


class TestResumenYBusquedaPorCampo(unittest.TestCase):
    def test_resumen_antes_de_guardar(self):
        out, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        self.assertIn("===== RESUMEN DE LA SOLICITUD =====", out)
        self.assertIn("Solicitante: Quispe Rojas, Mateo Alonso", out)
        self.assertIn("Folios: 6", out)
        self.assertLess(out.index("RESUMEN DE LA SOLICITUD"),
                        out.index("Codigo asignado"))

    def test_responder_n_en_el_resumen_no_guarda_nada(self):
        reg = REGISTRO_1[:-1] + ["N"]
        out, carpeta = ejecutar(["SEC-01"] + reg + ["0"])
        self.assertIn("Registro cancelado. No se guardo nada", out)
        self.assertNotIn("Codigo asignado", out)
        self.assertFalse(os.path.exists(os.path.join(carpeta, "Tramite.txt")))

    def test_confirmacion_repite_si_no_es_s_ni_n(self):
        reg = REGISTRO_1[:-1] + ["quizas", "S"]
        out, _ = ejecutar(["SEC-01"] + reg + ["0"])
        self.assertIn("Responda S (si) o N (no)", out)
        self.assertIn("Codigo asignado: SOL-001", out)

    def test_buscar_en_el_campo_elegido_y_resultado_en_tabla(self):
        # por DNI (campo 2): "ana" no esta en ningun DNI
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 +
                          ["2", "2", "45678912", "2", "2", "ana", "0"])
        self.assertIn("Coincidencias encontradas: 1", out)
        self.assertIn("Coincidencias encontradas: 0", out)
        filas = [l for l in out.splitlines() if l.startswith("| SOL-")]
        self.assertEqual(len(filas), 1)
        self.assertIn("Torres Vega", filas[0])
        self.assertIn("| CODIGO", out)

    def test_buscar_por_estado(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 + [
            "6", "1", "1", "Falta DNI",
            "2", "7", "en revision", "0"])
        self.assertIn("Coincidencias encontradas: 1", out)

    def test_texto_de_busqueda_obligatorio(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + ["2", "1", "", "SOL", "0"])
        self.assertIn("no puede quedar vacio", out)


class TestConfirmacionYRechazo(unittest.TestCase):
    OBSERVAR = ["6", "1", "1", "Documentos completos",
                "6", "1", "1", "Falta copia del DNI"]

    def test_pide_confirmar_antes_de_aprobar(self):
        out, carpeta = ejecutar(["DIR-01"] + REGISTRO_1 + self.OBSERVAR + [
            "6", "1", "1", "Todo conforme", "S", "0"])
        self.assertIn("Esta accion es definitiva", out)
        self.assertIn("quedara APROBADO", out)
        self.assertIn("Estado: Aprobado", out)

    def test_responder_n_cancela_la_aprobacion(self):
        out, carpeta = ejecutar(["DIR-01"] + REGISTRO_1 + self.OBSERVAR + [
            "6", "1", "1", "Todo conforme", "N", "0"])
        self.assertIn("Cambio cancelado", out)
        self.assertEqual(len(leer(carpeta, "Seguimiento.txt")), 3)

    def test_observar_no_pide_confirmacion(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + self.OBSERVAR + ["0"])
        self.assertNotIn("Esta accion es definitiva", out)

    def test_rechazo_exige_motivo_claro(self):
        out, carpeta = ejecutar(["DIR-01"] + REGISTRO_1 + self.OBSERVAR + [
            "6", "1", "2", "", "mal", "Documento ilegible y sin firma", "S",
            "0"])
        self.assertEqual(out.count("Al rechazar debe explicar el motivo"), 2)
        self.assertIn("quedara RECHAZADO", out)
        self.assertEqual(leer(carpeta, "Seguimiento.txt")[-1],
                         "1|Rechazado|4-11-26|15:59|"
                         "Documento ilegible y sin firma|DIR-01")


class TestPermisosPorCargo(unittest.TestCase):
    def test_tramite_txt_guarda_quien_registro(self):
        _, carpeta = ejecutar(["SEC-02"] + REGISTRO_1 + ["0"])
        _, carpeta = ejecutar(["DIR-01"] + REGISTRO_2 + ["0"],
                              carpeta=carpeta)
        lineas = leer(carpeta, "Tramite.txt")
        self.assertTrue(lineas[0].endswith("|6|SEC-02"))
        self.assertTrue(lineas[1].endswith("|3|DIR-01"))

    def _dos_secretarias_y_director(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + ["0"])
        _, carpeta = ejecutar(["SEC-02"] + REGISTRO_2 + ["0"], carpeta=carpeta)
        return carpeta

    def test_secretaria_solo_ve_lo_que_ella_registro(self):
        carpeta = self._dos_secretarias_y_director()
        out, _ = ejecutar(["SEC-01", "5", "0", "0"], carpeta=carpeta)
        self.assertIn("Quispe Rojas", out)
        self.assertNotIn("Torres Vega", out)
        self.assertIn("TOTAL DE EXPEDIENTES: 1", out)
        self.assertIn("Se cargaron 1 solicitud(es)", out)

    def test_secretaria_no_puede_abrir_ni_cambiar_lo_de_otra(self):
        carpeta = self._dos_secretarias_y_director()
        out, _ = ejecutar(["SEC-01", "5", "SOL-002", "0", "6", "SOL-002",
                           "0"], carpeta=carpeta)
        self.assertIn("No existe un expediente con ese codigo", out)
        self.assertIn("No existe una solicitud con ese codigo", out)
        self.assertEqual(len(leer(carpeta, "Seguimiento.txt")), 2)

    def test_buscar_y_ordenar_solo_entre_las_propias(self):
        carpeta = self._dos_secretarias_y_director()
        out, _ = ejecutar(["SEC-01", "2", "1", "SOL", "3", "1", "1", "0"],
                          carpeta=carpeta)
        self.assertIn("Coincidencias encontradas: 1", out)
        self.assertNotIn("Torres Vega", out)

    def test_reporte_de_la_secretaria_solo_cuenta_las_suyas(self):
        carpeta = self._dos_secretarias_y_director()
        out, _ = ejecutar(["SEC-01", "4", "0"], carpeta=carpeta)
        self.assertIn("TOTAL GENERAL: 1", out)

    def test_director_ve_todo(self):
        carpeta = self._dos_secretarias_y_director()
        out, _ = ejecutar(["DIR-01", "5", "0", "4", "0"], carpeta=carpeta)
        self.assertIn("TOTAL DE EXPEDIENTES: 2", out)
        self.assertIn("TOTAL GENERAL: 2", out)

    def test_archivo_antiguo_sin_registrador_solo_lo_ve_el_director(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with open(os.path.join(tmp.name, "Tramite.txt"), "w",
                  encoding="utf-8") as f:
            f.write("1|8-11-26|19:33|1|70726552|Vega Sanchez|Ariana|2\n")
        out, _ = ejecutar(["SEC-01", "5", "0", "0"], carpeta=tmp.name)
        self.assertNotIn("Vega Sanchez", out)
        out, _ = ejecutar(["DIR-01", "5", "0", "0"], carpeta=tmp.name)
        self.assertIn("Vega Sanchez", out)

    def test_responsable_se_recupera_al_reabrir(self):
        carpeta = self._dos_secretarias_y_director()
        out, _ = ejecutar(["DIR-01", "2", "1", "SOL-002", "0"],
                          carpeta=carpeta)
        fila = [l for l in out.splitlines() if l.startswith("| SOL-002")][0]
        self.assertIn("| SEC-02 ", fila)


class TestFormatoDeArchivos(unittest.TestCase):
    def test_numero_de_tramite_de_la_persona(self):
        # la misma persona (mismo DNI) registra tres veces: 1, 2 y 3
        reg2 = list(REGISTRO_1)
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + reg2 + REGISTRO_2
                              + reg2 + ["0"])
        campos = [l.split("|") for l in leer(carpeta, "Tramite.txt")]
        self.assertEqual([c[3] for c in campos], ["1", "2", "1", "3"])
        self.assertEqual([c[0] for c in campos],
                         ["SOL-001", "SOL-002", "SOL-003", "SOL-004"])

    def test_resumen_muestra_el_numero_de_tramite_de_la_persona(self):
        out, _ = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_1 + ["0"])
        self.assertIn("N.o de tramite de esta persona: 1", out)
        self.assertIn("N.o de tramite de esta persona: 2", out)

    def test_campos_vacios_se_guardan_con_guion(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_2 + ["0"])
        c = leer(carpeta, "Tramite.txt")[0].split("|")
        self.assertEqual(len(c), 14)
        self.assertEqual(c[9], "-")            # el egresado no tiene nivel

    def test_todos_los_datos_se_recuperan_al_reabrir(self):
        _, carpeta = ejecutar(["SEC-01"] + REGISTRO_1 + REGISTRO_2 + ["0"])
        out, _ = ejecutar(["SEC-01", "2", "3", "quispe", "2", "5",
                           "egresado", "0"], carpeta=carpeta)
        filas = [l for l in out.splitlines() if l.startswith("| SOL-")]
        self.assertEqual(len(filas), 2)
        self.assertIn("ESTUDIANTE", filas[0])
        self.assertIn("SECUNDARIA", filas[0])
        self.assertIn("987654321", filas[0])
        self.assertIn("EGRESADO", filas[1])
        self.assertIn("912345678", filas[1])
        self.assertIn("| SEC-01 ", filas[0])

    def test_seguimiento_guarda_el_responsable_del_cambio(self):
        _, carpeta = ejecutar(["SEC-02"] + REGISTRO_1 + [
            "6", "1", "1", "Documentos completos", "0"])
        self.assertEqual(leer(carpeta, "Seguimiento.txt"), [
            "1|Registrado|4-11-26|15:59|Solicitud registrada|SEC-02",
            "1|En revision|4-11-26|15:59|Documentos completos|SEC-02"])

    def test_se_leen_los_formatos_antiguos(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with open(os.path.join(tmp.name, "Tramite.txt"), "w",
                  encoding="utf-8") as f:
            f.write("1|8-11-26|19:33|1|70726552|Vega Sanchez|Ariana|2\n"
                    "2|8-11-26|19:35|2|70726552|Vega Sanchez|Ariana|3|SEC-01\n")
        with open(os.path.join(tmp.name, "Seguimiento.txt"), "w",
                  encoding="utf-8") as f:
            f.write("1|Registrado|8-11-26|19:33|Solicitud registrada\n")
        out, carpeta = ejecutar(["DIR-01", "5", "SOL-001", "0", "0"],
                                carpeta=tmp.name)
        self.assertIn("Se cargaron 2 solicitud(es)", out)
        self.assertIn("Remitente: Vega Sanchez, Ariana", out)
        # la numeracion sigue y la persona va por su 3.er tramite
        out, carpeta = ejecutar(["DIR-01", "1", "1", "70726552", "Vega Sanchez",
                                 "Ariana", "987654321", "3", "1", "1", "1",
                                 "S", "0"], carpeta=carpeta)
        self.assertIn("N.o de tramite de esta persona: 3", out)
        self.assertIn("Codigo asignado: SOL-003", out)


if __name__ == "__main__":
    unittest.main()


class PruebasPantalla(unittest.TestCase):
    """Limpiar pantalla en cada opcion y pausa de 'cualquier tecla'."""

    def test_limpia_y_espera_en_cada_opcion(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with mock.patch("builtins.input", side_effect=["SEC-01", "4", "0"]), \
                mock.patch.object(mp, "ARCHIVO_TRAMITE",
                                  os.path.join(tmp.name, "T.txt")), \
                mock.patch.object(mp, "ARCHIVO_SEGUIMIENTO",
                                  os.path.join(tmp.name, "S.txt")), \
                mock.patch.object(mp, "limpiar_pantalla") as limpiar, \
                mock.patch.object(mp, "esperar_tecla") as esperar, \
                redirect_stdout(io.StringIO()):
            mp.main()
        # menu (1) + opcion 4 (1) + menu otra vez (1) + opcion 0 (1)
        self.assertEqual(limpiar.call_count, 4)
        # bienvenida + fin de opcion 4 + salida
        self.assertEqual(esperar.call_count, 3)
        self.assertIn("salir", esperar.call_args_list[-1][0][0])

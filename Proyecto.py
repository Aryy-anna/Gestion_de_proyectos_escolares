"""Mesa de partes digital - I.E. N. 81770 "Maria Inmaculada Concepcion".

    Ejecutar:  py IE_MARIA_INMACULADA.py
"""
import os
import sys
from datetime import date, datetime

MAX_SOLICITUDES = 200
MAX_INTENTOS = 3

CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_TRAMITE = os.path.join(CARPETA, "Tramite.txt")
ARCHIVO_SEGUIMIENTO = os.path.join(CARPETA, "Seguimiento.txt")

# Tramites (posicion 1-6 del catalogo) que puede pedir cada condicion.
# 1 Constancia de estudios, 2 Certificado de estudios, 3 Matricula o traslado,
# 4 Justificacion de inasistencia, 5 Actualizacion de datos, 6 Otros
TRAMITES_ESTUDIANTE = [1, 2, 3, 4, 5, 6]
TRAMITES_EGRESADO = [1, 2, 5, 6]

CAT_ESTADOS = ["Registrado", "En revision", "Observado", "Aprobado",
               "Rechazado"]

# ------------------------------------------------------------------ ENTRADA
def leer_entero(mensaje):
    """Lee un entero. Si el usuario escribe texto, vuelve a pedirlo."""
    while True:
        texto = input(mensaje).strip()
        try:
            return int(texto)
        except ValueError:
            print("[!] Ingrese un numero entero.")


def leer_rango(mensaje, minimo, maximo):
    """Lee un entero entre minimo y maximo (inclusive)."""
    while True:
        valor = leer_entero(mensaje)
        if minimo <= valor <= maximo:
            return valor
        print("[!] Ingrese un numero entre " + str(minimo) + " y "
              + str(maximo) + ".")


def leer_no_vacio(mensaje):
    """Lee un texto y lo vuelve a pedir mientras este vacio."""
    while True:
        texto = input(mensaje).strip()
        if texto != "":
            return texto
        print("[!] Este dato no puede quedar vacio.")


def limpiar_texto(texto):
    """Quita el separador '|' para no romper el formato de los .txt."""
    return texto.replace("|", "/").strip()


# --------------------------------------------------------- FECHA Y CODIGOS
def obtener_fecha_sistema():
    """Fecha actual del sistema en formato AAAAMMDD (no la escribe el usuario)."""
    return date.today().strftime("%Y%m%d")


def obtener_hora_sistema():
    """Hora actual del sistema en formato HH:MM."""
    return datetime.now().strftime("%H:%M")


def formatear_fecha(fecha):
    """Convierte AAAAMMDD en DD/MM/AAAA."""
    return fecha[6:8] + "/" + fecha[4:6] + "/" + fecha[0:4]


def fecha_a_txt(fecha):
    """Convierte AAAAMMDD en el formato de los archivos: D-M-AA (4-11-26)."""
    return str(int(fecha[6:8])) + "-" + str(int(fecha[4:6])) + "-" + fecha[2:4]


def txt_a_fecha(texto):
    """Convierte D-M-AA en AAAAMMDD. Devuelve "" si el formato es invalido."""
    partes = texto.strip().split("-")
    if len(partes) != 3:
        return ""
    for p in partes:
        if not solo_digitos(p):
            return ""
    return "20" + partes[2].zfill(2) + partes[1].zfill(2) + partes[0].zfill(2)

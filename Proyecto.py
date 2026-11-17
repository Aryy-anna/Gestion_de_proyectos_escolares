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


def generar_codigo(n):
    # n < 10 -> "00n" ; n < 100 -> "0nn" ; si no -> "nnn"
    if n < 10:
        numero = "00" + str(n)
    elif n < 100:
        numero = "0" + str(n)
    else:
        numero = str(n)
    return "SOL-" + numero


def numero_de_codigo(codigo):
    """'SOL-007' -> 7."""
    return int(codigo[4:])

# -------------------------------------------------------------- VALIDACION
def solo_digitos(texto):
    # Se compara caracter por caracter; evita que str.isdigit() acepte
    # simbolos como "²".
    if len(texto) == 0:
        return False
    for c in texto:
        if c < "0" or c > "9":
            return False
    return True


def validar_dni(dni):
    return len(dni) == 8 and solo_digitos(dni)


def validar_telefono(tel):
    return len(tel) == 9 and solo_digitos(tel) and tel[0] == "9"


def contar_palabras(texto):
    cantidad = 0
    anterior = " "
    for c in texto:
        if c != " " and anterior == " ":
            cantidad += 1
        anterior = c
    return cantidad


def validar_nombre(texto):
    """Apellidos o nombres: al menos 2 caracteres y sin digitos ni '|'."""
    if len(texto.strip()) < 2:
        return False
    for c in texto:
        if ("0" <= c <= "9") or c == "|":
            return False
    return True

# ------------------------------------------------------------ ARCHIVOS .TXT
def guardar_tramite(ruta, numero, fecha, hora, motivo, dni, apellidos,
                    nombres, folio):
    """Agrega una linea a Tramite.txt:
    numero|fecha|hora|motivo|dni|apellidos|nombres|folio"""
    linea = "|".join([str(numero), fecha_a_txt(fecha), hora, str(motivo),
                      dni, limpiar_texto(apellidos), limpiar_texto(nombres),
                      str(folio)])
    try:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        return True
    except OSError:
        return False


def guardar_seguimiento(ruta, numero, fase, fecha, hora, motivo):
    """Agrega una linea a Seguimiento.txt: numero|fase|fecha|hora|motivo"""
    linea = "|".join([str(numero), fase, fecha_a_txt(fecha), hora,
                      limpiar_texto(motivo)])
    try:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        return True
    except OSError:
        return False


def cargar_tramites(ruta):
    """Lee Tramite.txt. Devuelve una lista de tuplas
    (numero, fecha AAAAMMDD, hora, motivo, dni, apellidos, nombres, folio).
    Las lineas con formato invalido se ignoran."""
    registros = []
    if not os.path.exists(ruta):
        return registros
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            c = linea.rstrip("\n").split("|")
            if len(c) != 8:
                continue
            fecha = txt_a_fecha(c[1])
            if (not solo_digitos(c[0]) or fecha == ""
                    or not solo_digitos(c[3]) or not solo_digitos(c[7])):
                continue
            registros.append((int(c[0]), fecha, c[2], int(c[3]), c[4], c[5],
                              c[6], int(c[7])))
    return registros


def cargar_seguimiento(ruta):
    """Lee Seguimiento.txt. Devuelve una lista de tuplas
    (numero, fase, fecha AAAAMMDD, hora, motivo)."""
    eventos = []
    if not os.path.exists(ruta):
        return eventos
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            c = linea.rstrip("\n").split("|")
            if len(c) < 4 or not solo_digitos(c[0]):
                continue
            fecha = txt_a_fecha(c[2])
            if fecha == "":
                continue
            motivo = c[4] if len(c) > 4 else ""
            eventos.append((int(c[0]), c[1].strip(), fecha, c[3], motivo))
    return eventos


def fase_del_catalogo(fase):
    """Devuelve la fase escrita como en CAT_ESTADOS (sin distinguir
    mayusculas) o la misma fase si no esta en el catalogo."""
    for e in CAT_ESTADOS:
        if e.upper() == fase.upper():
            return e
    return fase

# ------------------------------------------------------- ACCESO Y ESTADOS
def ingresar_acceso(cat_accesos):
    """Pide el codigo de acceso (hasta 3 intentos).
    Devuelve la posicion del codigo en el catalogo o -1 si se denegó."""
    intentos = 0
    posicion = -1

    while intentos < MAX_INTENTOS and posicion == -1:
        codigo = input("Codigo de acceso: ").strip().upper()

        for i in range(len(cat_accesos)):
            if cat_accesos[i] == codigo:
                posicion = i

        if posicion == -1:
            intentos += 1
            print("[!] Codigo incorrecto. Intentos restantes:",
                  MAX_INTENTOS - intentos)

    return posicion


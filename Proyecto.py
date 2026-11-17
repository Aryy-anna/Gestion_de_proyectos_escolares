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


def estado_permitido(actual, nuevo):
    """Cambios de estado permitidos:
    Registrado  -> En revision
    En revision -> Observado | Aprobado | Rechazado
    Observado   -> En revision | Aprobado | Rechazado
    Aprobado y Rechazado son estados finales."""
    permitido = False

    if actual == "Registrado":
        permitido = (nuevo == "En revision")
    if actual == "En revision":
        permitido = (nuevo == "Observado" or nuevo == "Aprobado"
                     or nuevo == "Rechazado")
    if actual == "Observado":
        permitido = (nuevo == "En revision" or nuevo == "Aprobado"
                     or nuevo == "Rechazado")

    return permitido


def buscar_posicion_codigo(codigos, n, codigo):
    """Busqueda lineal exacta por codigo (SOL-001) o por numero (1).
    Devuelve la posicion o -1."""
    codigo = codigo.strip().upper()
    if solo_digitos(codigo):
        codigo = generar_codigo(int(codigo))

    posicion = -1
    for i in range(n):
        if codigos[i] == codigo:
            posicion = i
    return posicion


def actualizar_estado(pos, estados, notas, cat_estados):
    """Cambia el estado de la solicitud en 'pos' respetando el flujo y pide
    el motivo. Devuelve (nuevo_estado, motivo) o ("", "") si no hubo cambio."""
    actual = estados[pos]
    print("Estado actual:", actual)

    hay_opciones = False
    print("ESTADOS DISPONIBLES")
    for j in range(len(cat_estados)):
        if estado_permitido(actual, cat_estados[j]):
            print(str(j + 1) + ". " + cat_estados[j])
            hay_opciones = True

    if not hay_opciones:
        print("La solicitud ya esta en un estado final (" + actual + ").")
        return "", ""

    while True:
        eleccion = leer_entero("Seleccione nuevo estado (0 = cancelar): ")
        if eleccion == 0:
            print("[!] Cambio cancelado.")
            return "", ""
        if 1 <= eleccion <= len(cat_estados) and estado_permitido(
                actual, cat_estados[eleccion - 1]):
            break
        print("[!] Cambio no permitido desde el estado " + actual + ".")

    nuevo = cat_estados[eleccion - 1]
    motivo = limpiar_texto(leer_no_vacio("Motivo del cambio a "
                                         + nuevo + ": "))
    if motivo == "":
        motivo = "Sin motivo"

    estados[pos] = nuevo
    notas[pos] = motivo
    return nuevo, motivo


# ---------------------------------------------------- BUSQUEDA Y ORDEN
def contiene_texto(texto, buscado):
    """Devuelve True si 'buscado' aparece dentro de 'texto' (sin distinguir
    mayusculas). Una busqueda vacia coincide con todo."""
    texto = texto.upper()
    buscado = buscado.upper()
    lb = len(buscado)

    if lb == 0:
        return True
    if lb <= len(texto):
        for i in range(len(texto) - lb + 1):
            if texto[i:i + lb] == buscado:
                return True
    return False


def busqueda_lineal(codigos, dnis, apellidos, nombres, grados, condiciones,
                    tramites, n, buscado):
    """Devuelve (encontrados, total, comparaciones)."""
    encontrados = [0] * MAX_SOLICITUDES
    total = 0
    comparaciones = 0

    for i in range(n):
        coincide = False
        k = 1

        while not coincide and k <= 7:
            if k == 1:
                campo = codigos[i]
            elif k == 2:
                campo = dnis[i]
            elif k == 3:
                campo = apellidos[i]
            elif k == 4:
                campo = nombres[i]
            elif k == 5:
                campo = grados[i]
            elif k == 6:
                campo = condiciones[i]
            else:
                campo = tramites[i]

            comparaciones += 1
            coincide = contiene_texto(campo, buscado)
            k += 1

        if coincide:
            encontrados[total] = i
            total += 1

    return encontrados, total, comparaciones


def armar_claves(claves, n, criterio, codigos, fechas, horas, apellidos,
                 nombres, niveles, tramites):
    for i in range(n):
        if criterio == 2:
            claves[i] = fechas[i] + horas[i]
        elif criterio == 3:
            claves[i] = apellidos[i].upper() + " " + nombres[i].upper()
        elif criterio == 4:
            claves[i] = niveles[i]
        elif criterio == 5:
            claves[i] = tramites[i]
        else:
            claves[i] = codigos[i]


def todas_las_posiciones(orden, n):
    for i in range(n):
        orden[i] = i


def ordenar_burbuja(orden, claves, n, ascendente):
    """Burbuja con bandera de parada anticipada.
    Devuelve (comparaciones, intercambios)."""
    todas_las_posiciones(orden, n)

    comparaciones = 0
    intercambios = 0
    i = 1
    hubo_intercambio = True

    while i <= n - 1 and hubo_intercambio:
        hubo_intercambio = False

        for j in range(n - i):
            comparaciones += 1

            if ascendente:
                desordenado = claves[orden[j]] > claves[orden[j + 1]]
            else:
                desordenado = claves[orden[j]] < claves[orden[j + 1]]

            if desordenado:
                orden[j], orden[j + 1] = orden[j + 1], orden[j]
                intercambios += 1
                hubo_intercambio = True

        i += 1

    return comparaciones, intercambios


# ------------------------------------------------- PRESENTACION Y REPORTES
def nombre_completo(pos, apellidos, nombres):
    return apellidos[pos] + ", " + nombres[pos]


def mostrar_solicitud(pos, codigos, fechas, horas, dnis, apellidos, nombres,
                      telefonos, niveles, grados, condiciones, tramites,
                      folios, estados, notas, responsables):
    nota = notas[pos]
    if nota == "":
        nota = "-"

    print("--------------------------------------------")
    print("Codigo de solicitud:", codigos[pos])
    print("Fecha de registro:", formatear_fecha(fechas[pos]), horas[pos])
    print("DNI del solicitante:", dnis[pos])
    print("Solicitante:", nombre_completo(pos, apellidos, nombres))
    print("Telefono de contacto:", telefonos[pos])
    print("Condicion:", condiciones[pos])
    print("Nivel educativo:", niveles[pos])
    print("Grado o edad:", grados[pos])
    print("Tipo de tramite:", tramites[pos])
    print("Folios:", folios[pos])
    print("Estado:", estados[pos])
    print("Motivo del estado:", nota)
    print("Personal responsable:", responsables[pos])


def listar_tramites(codigos, fechas, horas, tramites, apellidos, nombres,
                    estados, n):
    print("")
    print("===== LISTA DE TRAMITES / EXPEDIENTES =====")
    print("CODIGO | FECHA | TRAMITE | REMITENTE | ESTADO")
    for i in range(n):
        print(codigos[i] + " | " + formatear_fecha(fechas[i]) + " | "
              + tramites[i] + " | " + nombre_completo(i, apellidos, nombres)
              + " | " + estados[i])
    print("TOTAL DE EXPEDIENTES:", n)


def mostrar_expediente(pos, codigos, fechas, horas, dnis, apellidos, nombres,
                       tramites, folios, estados, notas, seguimiento):
    """Datos del remitente (nombre, DNI) y estado, mas el historial."""
    print("")
    print("===== EXPEDIENTE " + codigos[pos] + " =====")
    print("Remitente:", nombre_completo(pos, apellidos, nombres))
    print("DNI:", dnis[pos])
    print("Estado:", estados[pos])
    print("Motivo del estado:", notas[pos] if notas[pos] != "" else "-")
    print("Tramite:", tramites[pos])
    print("Registrado el:", formatear_fecha(fechas[pos]), horas[pos])
    print("Folios:", folios[pos])
    print("Seguimiento:")

    numero = numero_de_codigo(codigos[pos])
    for e in seguimiento:
        if e[0] == numero:
            texto = "  - " + formatear_fecha(e[2]) + " " + e[3] + " | " + e[1]
            if e[4] != "":
                texto = texto + " | " + e[4]
            print(texto)


def fila_del_tramite(tramite, cat_tramites):
    """Posicion del tramite en el catalogo; OTROS (ultima fila) por defecto."""
    fila = len(cat_tramites) - 1
    for i in range(len(cat_tramites)):
        if cat_tramites[i] == tramite:
            fila = i
    return fila


def reporte_documentos(tramites, estados, n, cat_tramites, cat_estados):
    ne = len(cat_estados)
    matriz = [[0] * ne for _ in range(6)]

    for k in range(n):
        fila = fila_del_tramite(tramites[k], cat_tramites)

        for j in range(ne):
            if cat_estados[j] == estados[k]:
                matriz[fila][j] += 1

    print("")
    print("===== REPORTE DE DOCUMENTOS =====")
    encabezado = "TRAMITE"
    for j in range(ne):
        encabezado = encabezado + " | " + cat_estados[j].upper()
    print(encabezado + " | TOTAL")

    for i in range(6):
        suma_fila = 0
        print(cat_tramites[i], end="")

        for j in range(ne):
            print(" | " + str(matriz[i][j]), end="")
            suma_fila += matriz[i][j]

        print(" | " + str(suma_fila))

    print("TOTAL GENERAL:", n)


"""Mesa de partes digital - I.E. N. 81770 "Maria Inmaculada Concepcion".

Ejecutar:  py IE_MARIA_INMACULADA.py
"""
import os
import shutil
import sys
from datetime import date, datetime

MAX_SOLICITUDES = 200
MAX_INTENTOS = 3
MIN_MOTIVO_RECHAZO = 10

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
CAT_TRAMITES = [
    "CONSTANCIA DE ESTUDIOS",
    "CERTIFICADO DE ESTUDIOS",
    "MATRICULA O TRASLADO",
    "JUSTIFICACION DE INASISTENCIA",
    "ACTUALIZACION DE DATOS",
    "OTROS",
]

# Estados que solo puede asignar el director (En revision y Observado los
# pueden asignar tambien las secretarias)
ESTADOS_DEL_DIRECTOR = ["Aprobado", "Rechazado"]


# ------------------------------------------------------------------ PANTALLA
def limpiar_pantalla():
    """Borra la consola (cls en Windows, clear en Linux/Mac)."""
    os.system("cls" if os.name == "nt" else "clear")


def esperar_tecla(mensaje="Presione cualquier tecla para continuar..."):
    """Pausa hasta que se toque cualquier tecla (sin necesidad de Enter)."""
    print("")
    print(mensaje, end="", flush=True)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.getwch()
        elif sys.stdin.isatty():
            import termios
            import tty
            fd = sys.stdin.fileno()
            anterior = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, anterior)
        else:
            sys.stdin.readline()
    except Exception:
        input()
    print("")


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


def leer_confirmacion(mensaje):
    """Pide S o N y devuelve True para S."""
    while True:
        texto = input(mensaje).strip().upper()
        if texto == "S" or texto == "SI":
            return True
        if texto == "N" or texto == "NO":
            return False
        print("[!] Responda S (si) o N (no).")


def leer_motivo_rechazo(mensaje):
    """El rechazo exige un motivo claro (minimo MIN_MOTIVO_RECHAZO letras),
    porque es lo que se le comunica al solicitante."""
    while True:
        texto = limpiar_texto(input(mensaje))
        if len(texto) >= MIN_MOTIVO_RECHAZO:
            return texto
        print("[!] Al rechazar debe explicar el motivo con claridad "
              "(minimo " + str(MIN_MOTIVO_RECHAZO) + " caracteres).")


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
def campo_txt(texto):
    """Texto listo para guardar: sin '|' y con '-' si esta vacio."""
    texto = limpiar_texto(str(texto))
    if texto == "":
        texto = "-"
    return texto


def guardar_tramite(ruta, codigo, fecha, hora, ordinal, dni, apellidos,
                    nombres, telefono, condicion, nivel, grado, tipo, folio,
                    registrador):
    """Agrega una linea a Tramite.txt (los campos vacios se guardan con "-"):
    codigo|fecha|hora|n.o de tramite de la persona|dni|apellidos|nombres|
    celular|condicion|nivel|grado o edad|tipo de tramite|folios|registrador"""
    campos = [codigo, fecha_a_txt(fecha), hora, ordinal, dni, apellidos,
              nombres, telefono, condicion, nivel, grado, tipo, folio,
              registrador]
    linea = "|".join([campo_txt(c) for c in campos])
    try:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        return True
    except OSError:
        return False


def guardar_seguimiento(ruta, numero, fase, fecha, hora, motivo,
                        responsable):
    """Agrega una linea a Seguimiento.txt:
    numero|fase|fecha|hora|motivo|responsable"""
    linea = "|".join([str(numero), fase, fecha_a_txt(fecha), hora,
                      campo_txt(motivo), campo_txt(responsable)])
    try:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        return True
    except OSError:
        return False


def cargar_tramites(ruta):
    """Lee Tramite.txt. Devuelve una lista de tuplas
    (numero, fecha AAAAMMDD, hora, n.o de tramite de la persona, dni,
    apellidos, nombres, celular, condicion, nivel, grado o edad, tipo de
    tramite, folios, registrador).
    Tambien se leen los formatos antiguos de 8 y 9 campos (los datos que no
    traian quedan en "-"). Las lineas con formato invalido se ignoran."""
    registros = []
    if not os.path.exists(ruta):
        return registros
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            c = linea.rstrip("\n").split("|")
            if len(c) == 14:
                fecha = txt_a_fecha(c[1])
                if (c[0][:4] != "SOL-" or not solo_digitos(c[0][4:])
                        or fecha == "" or not solo_digitos(c[12])):
                    continue
                ordinal = c[3] if solo_digitos(c[3]) else "-"
                registros.append((int(c[0][4:]), fecha, c[2], ordinal, c[4],
                                  c[5], c[6], c[7], c[8].upper(), c[9].upper(),
                                  c[10], c[11], int(c[12]),
                                  c[13].strip().upper()))
            elif len(c) == 8 or len(c) == 9:
                fecha = txt_a_fecha(c[1])
                if (not solo_digitos(c[0]) or fecha == ""
                        or not solo_digitos(c[3]) or not solo_digitos(c[7])):
                    continue
                tipo = CAT_TRAMITES[int(c[3]) - 1] if 1 <= int(c[3]) <= 6 \
                    else CAT_TRAMITES[5]
                registrador = c[8].strip().upper() if len(c) == 9 else "-"
                if registrador == "":
                    registrador = "-"
                registros.append((int(c[0]), fecha, c[2], "-", c[4], c[5],
                                  c[6], "-", "-", "-", "-", tipo, int(c[7]),
                                  registrador))
    return registros


def cargar_seguimiento(ruta):
    """Lee Seguimiento.txt. Devuelve una lista de tuplas
    (numero, fase, fecha AAAAMMDD, hora, motivo, responsable). Las lineas
    antiguas sin responsable se leen con "-"."""
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
            responsable = c[5].strip() if len(c) > 5 and c[5].strip() != "" \
                else "-"
            eventos.append((int(c[0]), c[1].strip(), fecha, c[3], motivo,
                            responsable))
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
    """Flujo de estados:
    Registrado  -> En revision
    En revision -> Observado
    Observado   -> Aprobado | Rechazado
    Aprobado y Rechazado son estados finales."""
    permitido = False

    if actual == "Registrado":
        permitido = (nuevo == "En revision")
    if actual == "En revision":
        permitido = (nuevo == "Observado")
    if actual == "Observado":
        permitido = (nuevo == "Aprobado" or nuevo == "Rechazado")

    return permitido


def puede_asignar(nuevo, es_director):
    """Aprobado y Rechazado solo los asigna el director."""
    return es_director or nuevo not in ESTADOS_DEL_DIRECTOR


def posiciones_visibles(registradores, n, codigo_acceso, es_director):
    """Posiciones que el usuario puede ver: el director ve todas y la
    secretaria solo las que ella registro."""
    visibles = []
    for i in range(n):
        if es_director or registradores[i] == codigo_acceso:
            visibles.append(i)
    return visibles


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


def actualizar_estado(pos, estados, notas, cat_estados, es_director=False,
                      codigo=""):
    """Cambia el estado de la solicitud en 'pos' respetando el flujo y pide
    el motivo. Aprobado y Rechazado solo se ofrecen al director.
    Devuelve (nuevo_estado, motivo) o ("", "") si no hubo cambio."""
    actual = estados[pos]
    print("Estado actual:", actual)

    siguientes = [e for e in cat_estados if estado_permitido(actual, e)]
    if len(siguientes) == 0:
        print("La solicitud ya esta en un estado final (" + actual + ").")
        return "", ""

    opciones = [e for e in siguientes if puede_asignar(e, es_director)]
    if len(opciones) == 0:
        print("[!] Solo el director puede aprobar o rechazar una solicitud "
              "observada.")
        return "", ""

    print("ESTADOS DISPONIBLES")
    for j in range(len(opciones)):
        print(str(j + 1) + ". " + opciones[j])

    while True:
        eleccion = leer_entero("Seleccione nuevo estado (0 = cancelar): ")
        if eleccion == 0:
            print("[!] Cambio cancelado.")
            return "", ""
        if 1 <= eleccion <= len(opciones):
            break
        print("[!] Opcion no valida.")

    nuevo = opciones[eleccion - 1]
    if nuevo == "Rechazado":
        motivo = leer_motivo_rechazo("Motivo del rechazo (obligatorio): ")
    else:
        motivo = limpiar_texto(leer_no_vacio("Motivo del cambio a "
                                             + nuevo + ": "))
        if motivo == "":
            motivo = "Sin motivo"

    if nuevo in ESTADOS_DEL_DIRECTOR:
        print("")
        print("Esta accion es definitiva: la solicitud " + codigo
              + " quedara " + nuevo.upper() + " y ya no se podra modificar.")
        if not leer_confirmacion("Confirmar (S/N): "):
            print("[!] Cambio cancelado.")
            return "", ""

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


CAMPOS_BUSQUEDA = ["Codigo", "DNI", "Apellidos y nombres", "Grado o edad",
                   "Condicion", "Tramite", "Estado"]


def valores_de_busqueda(campo, n, codigos, dnis, apellidos, nombres, grados,
                        condiciones, tramites, estados):
    """Devuelve la lista de valores del campo elegido (1-7), uno por solicitud."""
    valores = [""] * n
    for i in range(n):
        if campo == 1:
            valores[i] = codigos[i]
        elif campo == 2:
            valores[i] = dnis[i]
        elif campo == 3:
            valores[i] = apellidos[i] + " " + nombres[i]
        elif campo == 4:
            valores[i] = grados[i]
        elif campo == 5:
            valores[i] = condiciones[i]
        elif campo == 6:
            valores[i] = tramites[i]
        else:
            valores[i] = estados[i]
    return valores


def buscar_en_campo(posiciones, valores, buscado):
    """Busqueda lineal solo entre las 'posiciones' permitidas, comparando
    unicamente el campo elegido. Devuelve la lista de posiciones halladas."""
    encontrados = []
    for i in posiciones:
        if contiene_texto(valores[i], buscado):
            encontrados.append(i)
    return encontrados


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


def ordenar_burbuja(orden, claves, n, ascendente):
    """Burbuja con bandera de parada anticipada sobre las primeras n
    posiciones de 'orden' (que ya trae las posiciones permitidas).
    Devuelve (comparaciones, intercambios)."""

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


def mostrar_tabla(orden, n, codigos, fechas, horas, dnis, apellidos,
                  nombres, telefonos, niveles, grados, condiciones,
                  tramites, folios, estados, responsables):
    """Imprime las solicitudes como una tabla tipo Excel: una fila por
    solicitud, en el orden indicado por 'orden'. Las columnas se ajustan al
    contenido. CELULAR y RESPONSABLE solo se muestran si caben en la
    consola; si aun asi no cabe, se recortan SOLICITANTE y TRAMITE."""
    titulos = ["CODIGO", "FECHA Y HORA", "DNI", "SOLICITANTE", "CONDICION",
               "NIVEL", "GRADO", "TRAMITE", "FOLIOS", "ESTADO", "CELULAR",
               "RESPONSABLE"]
    COL_SOLICITANTE = 3
    COL_TRAMITE = 7
    COL_FOLIOS = 8
    MINIMO_TEXTO = 18

    filas = []
    for i in range(n):
        p = orden[i]
        # Del responsable solo se muestra el codigo de acceso: "(SEC-01)"
        resp = responsables[p]
        if "(" in resp:
            resp = resp[resp.rindex("(") + 1:].rstrip(")")
        filas.append([codigos[p],
                      fechas[p][6:8] + "/" + fechas[p][4:6] + "/"
                      + fechas[p][2:4] + " " + horas[p],
                      dnis[p], nombre_completo(p, apellidos, nombres),
                      condiciones[p], niveles[p], grados[p], tramites[p],
                      str(folios[p]), estados[p], telefonos[p], resp])

    anchos = [len(t) for t in titulos]
    for fila in filas:
        for c in range(len(titulos)):
            if len(fila[c]) > anchos[c]:
                anchos[c] = len(fila[c])

    limite = shutil.get_terminal_size((120, 30)).columns

    def ancho_total(cantidad):
        return sum(anchos[:cantidad]) + 3 * cantidad + 1

    # Se quitan primero las columnas opcionales (del final) si no caben
    columnas = len(titulos)
    while columnas > 10 and ancho_total(columnas) > limite:
        columnas -= 1

    # Si aun no cabe, se recortan los dos textos largos
    while ancho_total(columnas) > limite:
        c = COL_SOLICITANTE
        if anchos[COL_TRAMITE] > anchos[COL_SOLICITANTE]:
            c = COL_TRAMITE
        if anchos[c] <= MINIMO_TEXTO:
            break
        anchos[c] -= 1

    def linea(celdas):
        texto = "|"
        for c in range(columnas):
            t = celdas[c]
            if len(t) > anchos[c]:
                t = t[:anchos[c] - 2] + ".."
            if c == COL_FOLIOS:      # los numeros van a la derecha
                t = t.rjust(anchos[c])
            else:
                t = t.ljust(anchos[c])
            texto = texto + " " + t + " |"
        return texto

    borde = "+"
    for c in range(columnas):
        borde = borde + "-" * (anchos[c] + 2) + "+"

    print(borde)
    print(linea(titulos))
    print(borde)
    for fila in filas:
        print(linea(fila))
    print(borde)
    print("TOTAL DE SOLICITUDES:", n)


def listar_tramites(codigos, fechas, horas, tramites, apellidos, nombres,
                    estados, posiciones):
    print("")
    print("===== LISTA DE TRAMITES / EXPEDIENTES =====")
    print("CODIGO | FECHA | TRAMITE | REMITENTE | ESTADO")
    for i in posiciones:
        print(codigos[i] + " | " + formatear_fecha(fechas[i]) + " | "
              + tramites[i] + " | " + nombre_completo(i, apellidos, nombres)
              + " | " + estados[i])
    print("TOTAL DE EXPEDIENTES:", len(posiciones))


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
            if e[5] != "-":
                texto = texto + " | " + e[5]
            print(texto)


def fila_del_tramite(tramite, cat_tramites):
    """Posicion del tramite en el catalogo; OTROS (ultima fila) por defecto."""
    fila = len(cat_tramites) - 1
    for i in range(len(cat_tramites)):
        if cat_tramites[i] == tramite:
            fila = i
    return fila


def reporte_documentos(tramites, estados, posiciones, cat_tramites,
                       cat_estados):
    ne = len(cat_estados)
    matriz = [[0] * ne for _ in range(6)]

    for k in posiciones:
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

    print("TOTAL GENERAL:", len(posiciones))


# ------------------------------------------------------------- PROGRAMA
def main():
    # Arreglos paralelos (Dimension ...[200])
    codigos = [""] * MAX_SOLICITUDES
    fechas = [""] * MAX_SOLICITUDES
    horas = [""] * MAX_SOLICITUDES
    dnis = [""] * MAX_SOLICITUDES
    apellidos = [""] * MAX_SOLICITUDES
    nombres = [""] * MAX_SOLICITUDES
    telefonos = [""] * MAX_SOLICITUDES
    niveles = [""] * MAX_SOLICITUDES
    grados = [""] * MAX_SOLICITUDES
    condiciones = [""] * MAX_SOLICITUDES
    tramites = [""] * MAX_SOLICITUDES
    folios = [0] * MAX_SOLICITUDES
    estados = [""] * MAX_SOLICITUDES
    notas = [""] * MAX_SOLICITUDES
    responsables = [""] * MAX_SOLICITUDES
    registradores = [""] * MAX_SOLICITUDES   # codigo de acceso de quien registro
    ordinales = [""] * MAX_SOLICITUDES       # n.o de tramite de la persona
    claves = [""] * MAX_SOLICITUDES
    orden = [0] * MAX_SOLICITUDES

    # Historial de seguimiento: (numero, fase, fecha, hora, motivo)
    seguimiento = []

    cat_niveles = ["INICIAL", "PRIMARIA", "SECUNDARIA"]
    cat_condiciones = ["ESTUDIANTE", "EGRESADO"]
    cat_tramites = CAT_TRAMITES
    cat_estados = CAT_ESTADOS
    # Personal autorizado: el codigo de acceso identifica al responsable
    cat_accesos = ["SEC-01", "SEC-02", "DIR-01"]
    cat_personal = ["Mery Elizabeth Herrera Sanchez",
                    "Mailita Anali Julca Quezada",
                    "Luis Rafael Juarez Martinez"]
    cat_cargos = ["Secretaria", "Secretaria", "Director"]

    n = 0
    ultimo_numero = 0

    # ---- Carga de los archivos (si existen de una ejecucion anterior)
    # Tramite.txt no guarda telefono, nivel, grado, condicion ni
    # responsable: esos campos quedan en "-" para lo ya guardado.
    seguimiento = cargar_seguimiento(ARCHIVO_SEGUIMIENTO)
    for r in cargar_tramites(ARCHIVO_TRAMITE):
        if n >= MAX_SOLICITUDES:
            break
        codigos[n] = generar_codigo(r[0])
        fechas[n] = r[1]
        horas[n] = r[2]
        dnis[n] = r[4]
        apellidos[n] = r[5]
        nombres[n] = r[6]
        telefonos[n] = r[7]
        condiciones[n] = r[8]
        niveles[n] = r[9]
        grados[n] = r[10]
        tramites[n] = r[11]
        folios[n] = r[12]
        registradores[n] = r[13]
        # Si el archivo no trae el n.o de tramite de la persona (formato
        # antiguo), se cuenta cuantas solicitudes previas tiene ese DNI
        if r[3] == "-":
            previas = 0
            for k in range(n):
                if dnis[k] == r[4]:
                    previas += 1
            ordinales[n] = str(previas + 1)
        else:
            ordinales[n] = r[3]
        responsables[n] = "-"
        for k in range(len(cat_accesos)):
            if cat_accesos[k] == r[13]:
                responsables[n] = (cat_personal[k] + " (" + cat_accesos[k]
                                   + ")")
        estados[n] = "Registrado"
        notas[n] = ""
        for e in seguimiento:
            if e[0] == r[0]:
                estados[n] = fase_del_catalogo(e[1])
                notas[n] = e[4]
        if r[0] > ultimo_numero:
            ultimo_numero = r[0]
        n += 1

    print("================================================")
    print(" SISTEMA DE GESTION DE SOLICITUDES ESCOLARES")
    print(" I.E. N. 81770 MARIA INMACULADA CONCEPCION")
    print("================================================")

    persona = ingresar_acceso(cat_accesos)
    if persona == -1:
        print("Acceso denegado. Cerrando el sistema.")
        return

    responsable_actual = cat_personal[persona] + " (" + cat_accesos[persona] + ")"
    es_director = (cat_cargos[persona] == "Director")
    codigo_actual = cat_accesos[persona]
    SUFIJO_VACIO = "." if es_director else " por usted."
    print("Bienvenido(a): " + responsable_actual + " - " + cat_cargos[persona])
    propias = len(posiciones_visibles(registradores, n, codigo_actual,
                                      es_director))
    if propias > 0:
        print("Se cargaron " + str(propias) + " solicitud(es) de Tramite.txt.")
    esperar_tecla()

    while True:
        # Cada persona solo ve lo que le corresponde (la secretaria, lo que
        # ella registro; el director, todo)
        visibles = posiciones_visibles(registradores, n, codigo_actual,
                                       es_director)
        limpiar_pantalla()
        print("================================================")
        print(" SISTEMA DE GESTION DE SOLICITUDES ESCOLARES")
        print(" Personal: " + responsable_actual)
        print("================================================")
        print("1. Registrar solicitud escolar")
        print("2. Buscar solicitud")
        print("3. Ordenar solicitudes")
        print("4. Reporte de documentos")
        print("5. Lista de tramites")
        print("6. Actualizar estado de una solicitud")
        print("0. Salir")
        opcion = leer_entero("Seleccione una opcion: ")
        limpiar_pantalla()

        # ---------------------------------------------- 1. REGISTRAR
        if opcion == 1:
            if n >= MAX_SOLICITUDES or ultimo_numero >= 999:
                print("[!] Se alcanzo el maximo de solicitudes.")
            else:
                print("")
                print("================================================")
                print("        REGISTRO DE SOLICITUD ESCOLAR ")
                print("================================================")
                print("Escriba X en los campos iniciales para cancelar.")

                # Condicion (primera pregunta)
                print("")
                print("CONDICION")
                for i in range(2):
                    print(str(i + 1) + ". " + cat_condiciones[i])

                while True:
                    texto = input("Seleccione condicion (1-2): ").strip()
                    if texto.upper() == "X" or texto == "1" or texto == "2":
                        break
                    print("[!] Ingrese 1, 2 o X para cancelar.")
                if texto.upper() == "X":
                    print("[!] Registro cancelado.")
                    esperar_tecla()
                    continue
                condicion = cat_condiciones[int(texto) - 1]

                # DNI
                while True:
                    dni = input("DNI del solicitante (8 digitos): ").strip()
                    if dni.upper() != "X" and not validar_dni(dni):
                        print("[!] DNI invalido. Debe tener 8 digitos.")
                    if dni.upper() == "X" or validar_dni(dni):
                        break
                if dni.upper() == "X":
                    print("[!] Registro cancelado.")
                    esperar_tecla()
                    continue

                # Apellidos
                while True:
                    apellido = input("Apellidos del solicitante: ").strip()
                    if apellido.upper() != "X" and not validar_nombre(apellido):
                        print("[!] Ingrese los apellidos (sin numeros).")
                    if apellido.upper() == "X" or validar_nombre(apellido):
                        break
                if apellido.upper() == "X":
                    print("[!] Registro cancelado.")
                    esperar_tecla()
                    continue

                # Nombres
                while True:
                    nombre = input("Nombres del solicitante: ").strip()
                    if nombre.upper() != "X" and not validar_nombre(nombre):
                        print("[!] Ingrese los nombres (sin numeros).")
                    if nombre.upper() == "X" or validar_nombre(nombre):
                        break
                if nombre.upper() == "X":
                    print("[!] Registro cancelado.")
                    esperar_tecla()
                    continue

                # Telefono
                while True:
                    tel = input("Celular de contacto (9 digitos): ").strip()
                    if tel.upper() != "X" and not validar_telefono(tel):
                        print("[!] Debe tener 9 digitos y empezar con 9.")
                    if tel.upper() == "X" or validar_telefono(tel):
                        break
                if tel.upper() == "X":
                    print("[!] Registro cancelado.")
                    esperar_tecla()
                    continue

                if condicion == "ESTUDIANTE":
                    # Nivel (solo estudiantes)
                    print("")
                    print("NIVELES EDUCATIVOS")
                    for i in range(3):
                        print(str(i + 1) + ". " + cat_niveles[i])

                    while True:
                        criterio = leer_entero("Seleccione nivel (1-3): ")
                        if 1 <= criterio <= 3:
                            break
                    nivel = cat_niveles[criterio - 1]

                    # El estudiante solo indica el grado que cursa
                    if nivel == "INICIAL":
                        grado = str(leer_rango("Edad del aula (3, 4 o 5): ",
                                               3, 5))
                    elif nivel == "PRIMARIA":
                        grado = str(leer_rango("Grado que cursa (1-6): ",
                                               1, 6))
                    else:
                        grado = str(leer_rango("Grado que cursa (1-5): ",
                                               1, 5))
                else:
                    # El egresado no tiene nivel: pasa directo a su edad
                    nivel = "-"
                    grado = str(leer_rango("Edad: ", 10, 99))

                # Tramite (motivo): cada condicion ve solo los que le sirven
                if condicion == "ESTUDIANTE":
                    permitidos = TRAMITES_ESTUDIANTE
                else:
                    permitidos = TRAMITES_EGRESADO

                print("")
                print("TIPOS DE TRAMITE")
                for i in range(len(permitidos)):
                    print(str(i + 1) + ". " + cat_tramites[permitidos[i] - 1])

                while True:
                    eleccion = leer_entero("Seleccione tramite (1-"
                                           + str(len(permitidos)) + "): ")
                    if 1 <= eleccion <= len(permitidos):
                        break
                # 'motivo' es la posicion del tramite en el catalogo completo
                # (es el numero que se guarda en Tramite.txt)
                motivo = permitidos[eleccion - 1]
                tramite = cat_tramites[motivo - 1]

                # Folios (cantidad de hojas)
                while True:
                    folio = leer_entero("Folios (cantidad de hojas): ")
                    if folio >= 1:
                        break
                    print("[!] Debe tener al menos 1 folio.")

                # Resumen y confirmacion antes de guardar
                print("")
                print("===== RESUMEN DE LA SOLICITUD =====")
                print("Condicion:", condicion)
                print("DNI:", dni)
                print("Solicitante:", limpiar_texto(apellido) + ", "
                      + limpiar_texto(nombre))
                print("Celular:", tel)
                if condicion == "ESTUDIANTE":
                    print("Nivel educativo:", nivel)
                    print("Grado:", grado)
                else:
                    print("Edad:", grado)
                print("Tramite:", tramite)
                previas = 0
                for k in range(n):
                    if dnis[k] == dni:
                        previas += 1
                ordinal = previas + 1
                print("N.o de tramite de esta persona:", ordinal)
                print("Folios:", folio)
                print("Registrado por:", responsable_actual)
                if not leer_confirmacion("Confirmar y guardar (S/N): "):
                    print("[!] Registro cancelado. No se guardo nada.")
                    esperar_tecla()
                    continue

                # Fecha y hora las toma el sistema; el responsable sale del acceso
                fecha = obtener_fecha_sistema()
                hora = obtener_hora_sistema()
                ultimo_numero += 1
                codigo = generar_codigo(ultimo_numero)

                # Guardado (posicion n = siguiente libre; luego n += 1)
                codigos[n] = codigo
                fechas[n] = fecha
                horas[n] = hora
                dnis[n] = dni
                apellidos[n] = limpiar_texto(apellido)
                nombres[n] = limpiar_texto(nombre)
                telefonos[n] = tel
                niveles[n] = nivel
                grados[n] = grado
                condiciones[n] = condicion
                tramites[n] = tramite
                folios[n] = folio
                estados[n] = "Registrado"
                notas[n] = "Solicitud registrada"
                responsables[n] = responsable_actual
                registradores[n] = codigo_actual
                ordinales[n] = str(ordinal)
                n += 1

                # Archivos Tramite.txt y Seguimiento.txt
                ok1 = guardar_tramite(ARCHIVO_TRAMITE, codigo, fecha, hora,
                                      ordinal, dni, apellidos[n - 1],
                                      nombres[n - 1], tel, condicion, nivel,
                                      grado, tramite, folio, codigo_actual)
                seguimiento.append((ultimo_numero, "Registrado", fecha, hora,
                                    notas[n - 1], codigo_actual))
                ok2 = guardar_seguimiento(ARCHIVO_SEGUIMIENTO, ultimo_numero,
                                          "Registrado", fecha, hora,
                                          notas[n - 1], codigo_actual)

                print("")
                print("[OK] Solicitud registrada correctamente.")
                print("Codigo asignado:", codigo)
                print("Fecha y hora de registro:", formatear_fecha(fecha), hora)
                print("Estado inicial: Registrado")
                if not (ok1 and ok2):
                    print("[!] No se pudo escribir en los archivos .txt.")

        # ------------------------------------------------ 2. BUSCAR
        elif opcion == 2:
            if len(visibles) == 0:
                print("No hay solicitudes registradas" + SUFIJO_VACIO)
            else:
                print("")
                print("================================================")
                print("            BUSQUEDA DE SOLICITUDES")
                print("================================================")
                print("Buscar por:")
                for i in range(len(CAMPOS_BUSQUEDA)):
                    print(str(i + 1) + ". " + CAMPOS_BUSQUEDA[i])
                campo = leer_rango("Seleccione el campo (1-"
                                   + str(len(CAMPOS_BUSQUEDA)) + "): ", 1,
                                   len(CAMPOS_BUSQUEDA))
                buscado = leer_no_vacio("Texto a buscar en "
                                        + CAMPOS_BUSQUEDA[campo - 1].lower()
                                        + ": ")

                valores = valores_de_busqueda(campo, n, codigos, dnis,
                                              apellidos, nombres, grados,
                                              condiciones, tramites, estados)
                encontrados = buscar_en_campo(visibles, valores, buscado)

                print("")
                print("Coincidencias encontradas:", len(encontrados))
                if len(encontrados) > 0:
                    mostrar_tabla(encontrados, len(encontrados), codigos,
                                  fechas, horas, dnis, apellidos, nombres,
                                  telefonos, niveles, grados, condiciones,
                                  tramites, folios, estados, responsables)

        # ------------------------------------------------ 3. ORDENAR
        elif opcion == 3:
            if len(visibles) == 0:
                print("No hay solicitudes para ordenar.")
            else:
                print("")
                print("================================================")
                print("         ORDENAMIENTO DE SOLICITUDES")
                print("================================================")
                print("1. Codigo")
                print("2. Fecha")
                print("3. Nombre del solicitante")
                print("4. Nivel educativo")
                print("5. Tipo de tramite")

                while True:
                    criterio = leer_entero("Seleccione criterio (1-5): ")
                    if 1 <= criterio <= 5:
                        break

                armar_claves(claves, n, criterio, codigos, fechas, horas,
                             apellidos, nombres, niveles, tramites)

                print("1. Ascendente")
                print("2. Descendente")

                while True:
                    direccion = leer_entero("Seleccione direccion: ")
                    if direccion == 1 or direccion == 2:
                        break

                ascendente = (direccion == 1)

                for k in range(len(visibles)):
                    orden[k] = visibles[k]
                ordenar_burbuja(orden, claves, len(visibles), ascendente)
                print("")

                mostrar_tabla(orden, len(visibles), codigos, fechas, horas, dnis,
                              apellidos, nombres, telefonos, niveles, grados,
                              condiciones, tramites, folios, estados,
                              responsables)

        # ------------------------------------------------ 4. REPORTE
        elif opcion == 4:
            reporte_documentos(tramites, estados, visibles, cat_tramites,
                               cat_estados)

        # ------------------------------------------------ 5. LISTA / EXPEDIENTE
        elif opcion == 5:
            if len(visibles) == 0:
                print("No hay solicitudes registradas" + SUFIJO_VACIO)
            else:
                listar_tramites(codigos, fechas, horas, tramites, apellidos,
                                nombres, estados, visibles)

                while True:
                    texto = input("Codigo o numero del expediente a abrir "
                                  "(0 = volver): ").strip()
                    if texto == "0" or texto == "":
                        break
                    pos = buscar_posicion_codigo(codigos, n, texto)
                    if pos == -1 or pos not in visibles:
                        print("[!] No existe un expediente con ese codigo.")
                    else:
                        mostrar_expediente(pos, codigos, fechas, horas, dnis,
                                           apellidos, nombres, tramites,
                                           folios, estados, notas, seguimiento)

        # ------------------------------------------------ 6. ESTADO
        elif opcion == 6:
            if len(visibles) == 0:
                print("No hay solicitudes registradas" + SUFIJO_VACIO)
            else:
                print("")
                print("================================================")
                print("              ACTUALIZAR ESTADO")
                print("================================================")
                codigo = input("Codigo de la solicitud (ej. SOL-001 o 1): ")
                pos = buscar_posicion_codigo(codigos, n, codigo)

                if pos == -1 or pos not in visibles:
                    print("[!] No existe una solicitud con ese codigo.")
                else:
                    nuevo, motivo = actualizar_estado(pos, estados, notas,
                                                      cat_estados,
                                                      es_director,
                                                      codigos[pos])
                    if nuevo != "":
                        fecha = obtener_fecha_sistema()
                        hora = obtener_hora_sistema()
                        numero = numero_de_codigo(codigos[pos])
                        seguimiento.append((numero, nuevo, fecha, hora,
                                            motivo, codigo_actual))
                        ok = guardar_seguimiento(ARCHIVO_SEGUIMIENTO, numero,
                                                 nuevo, fecha, hora, motivo,
                                                 codigo_actual)
                        print("[OK] Estado actualizado.")
                        if not ok:
                            print("[!] No se pudo escribir Seguimiento.txt.")
                        mostrar_solicitud(pos, codigos, fechas, horas, dnis,
                                          apellidos, nombres, telefonos,
                                          niveles, grados, condiciones,
                                          tramites, folios, estados, notas,
                                          responsables)

        # ------------------------------------------------ 0. SALIR
        elif opcion == 0:
            print("Saliendo del sistema de gestion escolar...")
            esperar_tecla("Presione cualquier tecla para salir...")
            break

        else:
            print("[!] Opcion no valida.")

        # Cada opcion termina con una pausa; luego se limpia y vuelve el menu
        esperar_tecla()


if __name__ == "__main__":
    main()

"""Mesa de partes digital - I.E. N. 81770 "Maria Inmaculada Concepcion".

Prototipo de consola (Alternativa B): arreglos paralelos en memoria,
acceso por codigo de personal, flujo de estados y reportes.
Ejecutar:  python mesa_de_partes.py
"""
from datetime import date

MAX_SOLICITUDES = 200
MAX_INTENTOS = 3


# ------------------------------------------------------------------ ENTRADA
def leer_entero(mensaje):
    """Lee un entero. Si el usuario escribe texto, vuelve a pedirlo."""
    while True:
        texto = input(mensaje).strip()
        try:
            return int(texto)
        except ValueError:
            print("[!] Ingrese un numero entero.")


def leer_no_vacio(mensaje):
    """Lee un texto y lo vuelve a pedir mientras este vacio."""
    while True:
        texto = input(mensaje).strip()
        if texto != "":
            return texto
        print("[!] Este dato no puede quedar vacio.")


# --------------------------------------------------------- FECHA Y CODIGOS
def obtener_fecha_sistema():
    """Fecha actual del sistema en formato AAAAMMDD (no la escribe el usuario)."""
    return date.today().strftime("%Y%m%d")


def formatear_fecha(fecha):
    """Convierte AAAAMMDD en DD/MM/AAAA."""
    return fecha[6:8] + "/" + fecha[4:6] + "/" + fecha[0:4]


def generar_codigo(n):
    # n < 10 -> "00n" ; n < 100 -> "0nn" ; si no -> "nnn"
    if n < 10:
        numero = "00" + str(n)
    elif n < 100:
        numero = "0" + str(n)
    else:
        numero = str(n)
    return "SOL-" + numero


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


def validar_nombre(nombre):
    return len(nombre) >= 5 and contar_palabras(nombre) >= 2


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
    """Flujo del tramite: RECIBIDO > EN REVISION > (OBSERVADO | ATENDIDO).
    Una solicitud OBSERVADA vuelve a EN REVISION; ATENDIDO es final."""
    permitido = False

    if actual == "RECIBIDO":
        permitido = (nuevo == "EN REVISION")
    if actual == "EN REVISION":
        permitido = (nuevo == "OBSERVADO" or nuevo == "ATENDIDO")
    if actual == "OBSERVADO":
        permitido = (nuevo == "EN REVISION")

    return permitido


def buscar_posicion_codigo(codigos, n, codigo):
    """Busqueda lineal exacta por codigo. Devuelve la posicion o -1."""
    posicion = -1
    for i in range(n):
        if codigos[i] == codigo.strip().upper():
            posicion = i
    return posicion


def actualizar_estado(pos, estados, resultados, notas, codigos, fechas, dnis,
                      nombres, telefonos, niveles, grados, condiciones,
                      tramites, responsables, cat_estados, cat_resultados):
    """Cambia el estado de la solicitud en 'pos' respetando el flujo."""
    actual = estados[pos]
    print("Estado actual:", actual)

    if actual == "ATENDIDO":
        print("La solicitud ya fue atendida (" + resultados[pos] + ").")
        return

    print("ESTADOS DISPONIBLES")
    for j in range(4):
        if estado_permitido(actual, cat_estados[j]):
            print(str(j + 1) + ". " + cat_estados[j])

    while True:
        eleccion = leer_entero("Seleccione nuevo estado (0 = cancelar): ")
        if eleccion == 0:
            print("[!] Cambio cancelado.")
            return
        if 1 <= eleccion <= 4 and estado_permitido(actual,
                                                   cat_estados[eleccion - 1]):
            break
        print("[!] Cambio no permitido desde el estado " + actual + ".")

    nuevo = cat_estados[eleccion - 1]

    if nuevo == "OBSERVADO":
        notas[pos] = leer_no_vacio("Nota de observacion: ")

    if nuevo == "ATENDIDO":
        print("RESULTADO")
        print("1. " + cat_resultados[0])
        print("2. " + cat_resultados[1])
        while True:
            eleccion = leer_entero("Seleccione resultado (1-2): ")
            if eleccion == 1 or eleccion == 2:
                break
        resultados[pos] = cat_resultados[eleccion - 1]

        if resultados[pos] == "RECHAZADO":
            notas[pos] = leer_no_vacio("Motivo del rechazo (nota): ")

    estados[pos] = nuevo
    print("[OK] Estado actualizado.")
    mostrar_solicitud(pos, codigos, fechas, dnis, nombres, telefonos, niveles,
                      grados, condiciones, tramites, estados, resultados,
                      notas, responsables)


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


def busqueda_lineal(codigos, dnis, nombres, grados, condiciones, tramites,
                    n, buscado):
    """Devuelve (encontrados, total, comparaciones)."""
    encontrados = [0] * MAX_SOLICITUDES
    total = 0
    comparaciones = 0

    for i in range(n):
        coincide = False
        k = 1

        while not coincide and k <= 6:
            if k == 1:
                campo = codigos[i]
            elif k == 2:
                campo = dnis[i]
            elif k == 3:
                campo = nombres[i]
            elif k == 4:
                campo = grados[i]
            elif k == 5:
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


def armar_claves(claves, n, criterio, codigos, fechas, nombres, niveles,
                 tramites):
    for i in range(n):
        if criterio == 2:
            claves[i] = fechas[i]
        elif criterio == 3:
            claves[i] = nombres[i].upper()
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


def ordenar_insercion(orden, claves, n, ascendente):
    """Insercion directa. Devuelve (comparaciones, desplazamientos)."""
    todas_las_posiciones(orden, n)

    comparaciones = 0
    desplazamientos = 0

    for i in range(1, n):
        actual = orden[i]
        j = i - 1
        debe_correrse = True

        while j >= 0 and debe_correrse:
            comparaciones += 1

            if ascendente:
                debe_correrse = claves[orden[j]] > claves[actual]
            else:
                debe_correrse = claves[orden[j]] < claves[actual]

            if debe_correrse:
                orden[j + 1] = orden[j]
                desplazamientos += 1
                j -= 1

        orden[j + 1] = actual

    return comparaciones, desplazamientos


# ------------------------------------------------- PRESENTACION Y REPORTES
def mostrar_solicitud(pos, codigos, fechas, dnis, nombres, telefonos,
                      niveles, grados, condiciones, tramites, estados,
                      resultados, notas, responsables):
    estado = estados[pos]
    if resultados[pos] != "":
        estado = estado + " - " + resultados[pos]

    nota = notas[pos]
    if nota == "":
        nota = "-"

    print("--------------------------------------------")
    print("Codigo de solicitud:", codigos[pos])
    print("Fecha de registro:", formatear_fecha(fechas[pos]))
    print("DNI del estudiante:", dnis[pos])
    print("Estudiante:", nombres[pos])
    print("Telefono de contacto:", telefonos[pos])
    print("Nivel educativo:", niveles[pos])
    print("Grado o edad:", grados[pos])
    print("Condicion:", condiciones[pos])
    print("Tipo de tramite:", tramites[pos])
    print("Estado:", estado)
    print("Nota de observacion:", nota)
    print("Personal responsable:", responsables[pos])


def fila_del_tramite(tramite, cat_tramites):
    """Posicion del tramite en el catalogo; OTROS (ultima fila) por defecto."""
    fila = len(cat_tramites) - 1
    for i in range(len(cat_tramites)):
        if cat_tramites[i] == tramite:
            fila = i
    return fila


def reporte_tramite_estado(tramites, estados, resultados, n, cat_tramites,
                           cat_estados):
    # matriz[6][4] inicializada en 0
    matriz = [[0] * 4 for _ in range(6)]
    aprobados = 0
    rechazados = 0

    for k in range(n):
        fila = fila_del_tramite(tramites[k], cat_tramites)

        for j in range(4):
            if cat_estados[j] == estados[k]:
                matriz[fila][j] += 1

        if resultados[k] == "APROBADO":
            aprobados += 1
        if resultados[k] == "RECHAZADO":
            rechazados += 1

    print("")
    print("===== REPORTE POR TRAMITE Y ESTADO =====")
    print("TRAMITE | RECIBIDO | EN REVISION | OBSERVADO | ATENDIDO | TOTAL")

    for i in range(6):
        suma_fila = 0
        print(cat_tramites[i], end="")

        for j in range(4):
            print(" | " + str(matriz[i][j]), end="")
            suma_fila += matriz[i][j]

        print(" | " + str(suma_fila))

    print("TOTAL GENERAL:", n)
    print("Atendidos: " + str(aprobados) + " aprobados y " + str(rechazados)
          + " rechazados")


def reporte_documentos(tramites, estados, resultados, n, cat_tramites):
    solicitados = [0] * 6
    en_tramite = [0] * 6
    aprobados = [0] * 6
    rechazados = [0] * 6

    for k in range(n):
        fila = fila_del_tramite(tramites[k], cat_tramites)
        solicitados[fila] += 1

        if estados[k] != "ATENDIDO":
            en_tramite[fila] += 1
        elif resultados[k] == "APROBADO":
            aprobados[fila] += 1
        else:
            rechazados[fila] += 1

    print("")
    print("===== REPORTE DE DOCUMENTOS =====")
    print("DOCUMENTO | SOLICITADOS | EN TRAMITE | APROBADOS | RECHAZADOS")

    for i in range(6):
        print(cat_tramites[i] + " | " + str(solicitados[i]) + " | "
              + str(en_tramite[i]) + " | " + str(aprobados[i]) + " | "
              + str(rechazados[i]))

    print("TOTAL | " + str(sum(solicitados)) + " | " + str(sum(en_tramite))
          + " | " + str(sum(aprobados)) + " | " + str(sum(rechazados)))


def indice_ingresos(codigos, fechas, n):
    dias = [""] * MAX_SOLICITUDES
    cantidades = [0] * MAX_SOLICITUDES
    total_dias = 0

    for k in range(n):
        pos = -1
        for d in range(total_dias):
            if dias[d] == fechas[k]:
                pos = d

        if pos == -1:
            dias[total_dias] = fechas[k]
            cantidades[total_dias] = 0
            pos = total_dias
            total_dias += 1

        cantidades[pos] += 1

    print("")
    print("===== INDICE DE INGRESOS =====")
    print("FECHA | INGRESOS | % DEL TOTAL | CODIGOS")

    for d in range(total_dias):
        lista = ""
        for k in range(n):
            if fechas[k] == dias[d]:
                if lista != "":
                    lista = lista + ", "
                lista = lista + codigos[k]

        porcentaje = round(cantidades[d] * 1000 / n) / 10
        print(formatear_fecha(dias[d]) + " | " + str(cantidades[d]) + " | "
              + format(porcentaje, ".1f") + "% | " + lista)

    print("TOTAL DE INGRESOS:", n)


# ------------------------------------------------------------- PROGRAMA
def main():
    # Arreglos paralelos (Dimension ...[200])
    codigos = [""] * MAX_SOLICITUDES
    fechas = [""] * MAX_SOLICITUDES
    dnis = [""] * MAX_SOLICITUDES
    nombres = [""] * MAX_SOLICITUDES
    telefonos = [""] * MAX_SOLICITUDES
    niveles = [""] * MAX_SOLICITUDES
    grados = [""] * MAX_SOLICITUDES
    condiciones = [""] * MAX_SOLICITUDES
    tramites = [""] * MAX_SOLICITUDES
    estados = [""] * MAX_SOLICITUDES
    resultados = [""] * MAX_SOLICITUDES
    notas = [""] * MAX_SOLICITUDES
    responsables = [""] * MAX_SOLICITUDES
    claves = [""] * MAX_SOLICITUDES
    orden = [0] * MAX_SOLICITUDES

    cat_niveles = ["INICIAL", "PRIMARIA", "SECUNDARIA"]
    cat_condiciones = ["ESTUDIANTE", "EGRESADO"]
    cat_tramites = [
        "CONSTANCIA DE ESTUDIOS",
        "CERTIFICADO DE ESTUDIOS",
        "MATRICULA O TRASLADO",
        "JUSTIFICACION DE INASISTENCIA",
        "ACTUALIZACION DE DATOS",
        "OTROS",
    ]
    cat_estados = ["RECIBIDO", "EN REVISION", "OBSERVADO", "ATENDIDO"]
    cat_resultados = ["APROBADO", "RECHAZADO"]
    # Personal autorizado: el codigo de acceso identifica al responsable
    cat_accesos = ["SEC-01", "SEC-02", "DIR-01"]
    cat_personal = ["Mery Elizabeth Herrera Sanchez",
                    "Mailita Anali Julca Quezada",
                    "Luis Rafael Juarez Martinez"]

    n = 0

    print("================================================")
    print(" SISTEMA DE GESTION DE SOLICITUDES ESCOLARES")
    print(" I.E. N. 81770 MARIA INMACULADA CONCEPCION")
    print("================================================")

    persona = ingresar_acceso(cat_accesos)
    if persona == -1:
        print("Acceso denegado. Cerrando el sistema.")
        return

    responsable_actual = cat_personal[persona] + " (" + cat_accesos[persona] + ")"
    print("Bienvenido(a): " + responsable_actual)

    while True:
        print("")
        print("================================================")
        print(" SISTEMA DE GESTION DE SOLICITUDES ESCOLARES")
        print(" Personal: " + responsable_actual)
        print("================================================")
        print("1. Registrar solicitud escolar")
        print("2. Buscar solicitud")
        print("3. Ordenar solicitudes")
        print("4. Reporte por tramite y estado")
        print("5. Mostrar todas las solicitudes")
        print("6. Actualizar estado de una solicitud")
        print("7. Reporte de documentos")
        print("8. Indice de ingresos")
        print("0. Salir")
        opcion = leer_entero("Seleccione una opcion: ")

        # ---------------------------------------------- 1. REGISTRAR
        if opcion == 1:
            if n >= MAX_SOLICITUDES:
                print("[!] Se alcanzo el maximo de 200 solicitudes.")
            else:
                print("")
                print("===== REGISTRO DE SOLICITUD ESCOLAR =====")
                print("Escriba X en los campos iniciales para cancelar.")

                # DNI
                while True:
                    dni = input("DNI del estudiante (8 digitos): ")
                    if dni.upper() != "X" and not validar_dni(dni):
                        print("[!] DNI invalido. Debe tener 8 digitos.")
                    if dni.upper() == "X" or validar_dni(dni):
                        break
                if dni.upper() == "X":
                    print("[!] Registro cancelado.")
                    continue

                # Nombre
                while True:
                    nombre = input("Nombres y apellidos del estudiante: ")
                    if nombre.upper() != "X" and not validar_nombre(nombre):
                        print("[!] Ingrese nombres y apellidos.")
                    if nombre.upper() == "X" or validar_nombre(nombre):
                        break
                if nombre.upper() == "X":
                    print("[!] Registro cancelado.")
                    continue

                # Telefono
                while True:
                    tel = input("Celular de contacto (9 digitos): ")
                    if tel.upper() != "X" and not validar_telefono(tel):
                        print("[!] Debe tener 9 digitos y empezar con 9.")
                    if tel.upper() == "X" or validar_telefono(tel):
                        break
                if tel.upper() == "X":
                    print("[!] Registro cancelado.")
                    continue

                # Nivel
                print("")
                print("NIVELES EDUCATIVOS")
                for i in range(3):
                    print(str(i + 1) + ". " + cat_niveles[i])

                while True:
                    criterio = leer_entero("Seleccione nivel (1-3): ")
                    if 1 <= criterio <= 3:
                        break
                nivel = cat_niveles[criterio - 1]

                grado = leer_no_vacio("Grado o edad: ")

                # Condicion (reemplaza a la seccion)
                print("")
                print("CONDICION")
                for i in range(2):
                    print(str(i + 1) + ". " + cat_condiciones[i])

                while True:
                    criterio = leer_entero("Seleccione condicion (1-2): ")
                    if 1 <= criterio <= 2:
                        break
                condicion = cat_condiciones[criterio - 1]

                # Tramite
                print("")
                print("TIPOS DE TRAMITE")
                for i in range(6):
                    print(str(i + 1) + ". " + cat_tramites[i])

                while True:
                    criterio = leer_entero("Seleccione tramite (1-6): ")
                    if 1 <= criterio <= 6:
                        break
                tramite = cat_tramites[criterio - 1]

                # La fecha la toma el sistema y el responsable sale del acceso
                fecha = obtener_fecha_sistema()
                codigo = generar_codigo(n + 1)

                # Guardado (posicion n = siguiente libre; luego n += 1)
                codigos[n] = codigo
                fechas[n] = fecha
                dnis[n] = dni
                nombres[n] = nombre
                telefonos[n] = tel
                niveles[n] = nivel
                grados[n] = grado
                condiciones[n] = condicion
                tramites[n] = tramite
                estados[n] = "RECIBIDO"
                resultados[n] = ""
                notas[n] = ""
                responsables[n] = responsable_actual
                n += 1

                print("")
                print("[OK] Solicitud registrada correctamente.")
                print("Codigo asignado:", codigo)
                print("Fecha de registro:", formatear_fecha(fecha))
                print("Estado inicial: RECIBIDO")

        # ------------------------------------------------ 2. BUSCAR
        elif opcion == 2:
            if n == 0:
                print("No hay solicitudes registradas.")
            else:
                print("")
                print("===== BUSQUEDA DE SOLICITUDES =====")
                print("Ingrese codigo, DNI, nombre, grado, condicion o tramite:")
                buscado = input()

                encontrados, total, comparaciones = busqueda_lineal(
                    codigos, dnis, nombres, grados, condiciones, tramites,
                    n, buscado)

                print("Coincidencias encontradas:", total)
                print("Comparaciones realizadas:", comparaciones)

                for i in range(total):
                    mostrar_solicitud(encontrados[i], codigos, fechas, dnis,
                                      nombres, telefonos, niveles, grados,
                                      condiciones, tramites, estados,
                                      resultados, notas, responsables)

        # ------------------------------------------------ 3. ORDENAR
        elif opcion == 3:
            if n == 0:
                print("No hay solicitudes para ordenar.")
            else:
                print("")
                print("===== ORDENAMIENTO DE SOLICITUDES =====")
                print("1. Codigo")
                print("2. Fecha")
                print("3. Nombre del estudiante")
                print("4. Nivel educativo")
                print("5. Tipo de tramite")

                while True:
                    criterio = leer_entero("Seleccione criterio (1-5): ")
                    if 1 <= criterio <= 5:
                        break

                armar_claves(claves, n, criterio, codigos, fechas, nombres,
                             niveles, tramites)

                print("1. Ascendente")
                print("2. Descendente")

                while True:
                    direccion = leer_entero("Seleccione direccion: ")
                    if direccion == 1 or direccion == 2:
                        break

                ascendente = (direccion == 1)

                print("1. Metodo burbuja")
                print("2. Metodo insercion")

                while True:
                    metodo = leer_entero("Seleccione metodo: ")
                    if metodo == 1 or metodo == 2:
                        break

                if metodo == 1:
                    comparaciones, movimientos = ordenar_burbuja(
                        orden, claves, n, ascendente)
                else:
                    comparaciones, movimientos = ordenar_insercion(
                        orden, claves, n, ascendente)

                print("")
                print("Ordenamiento aplicado correctamente.")
                print("Comparaciones:", comparaciones)
                print("Intercambios o desplazamientos:", movimientos)

                for i in range(n):
                    mostrar_solicitud(orden[i], codigos, fechas, dnis,
                                      nombres, telefonos, niveles, grados,
                                      condiciones, tramites, estados,
                                      resultados, notas, responsables)

        # ------------------------------------------------ 4. REPORTE
        elif opcion == 4:
            reporte_tramite_estado(tramites, estados, resultados, n,
                                   cat_tramites, cat_estados)

        # ------------------------------------------------ 5. LISTAR
        elif opcion == 5:
            if n == 0:
                print("No hay solicitudes registradas.")
            else:
                print("")
                print("===== LISTADO DE SOLICITUDES ESCOLARES =====")
                for i in range(n):
                    mostrar_solicitud(i, codigos, fechas, dnis, nombres,
                                      telefonos, niveles, grados, condiciones,
                                      tramites, estados, resultados, notas,
                                      responsables)

        # ------------------------------------------------ 6. ESTADO
        elif opcion == 6:
            if n == 0:
                print("No hay solicitudes registradas.")
            else:
                print("")
                print("===== ACTUALIZAR ESTADO =====")
                codigo = input("Codigo de la solicitud (ej. SOL-001): ")
                pos = buscar_posicion_codigo(codigos, n, codigo)

                if pos == -1:
                    print("[!] No existe una solicitud con ese codigo.")
                else:
                    actualizar_estado(pos, estados, resultados, notas,
                                      codigos, fechas, dnis, nombres,
                                      telefonos, niveles, grados, condiciones,
                                      tramites, responsables, cat_estados,
                                      cat_resultados)

        # ------------------------------------------------ 7. DOCUMENTOS
        elif opcion == 7:
            reporte_documentos(tramites, estados, resultados, n, cat_tramites)

        # ------------------------------------------------ 8. INGRESOS
        elif opcion == 8:
            if n == 0:
                print("No hay solicitudes registradas.")
            else:
                indice_ingresos(codigos, fechas, n)

        # ------------------------------------------------ 0. SALIR
        elif opcion == 0:
            print("Saliendo del sistema de gestion escolar...")
            break

        else:
            print("[!] Opcion no valida.")


if __name__ == "__main__":
    main()

# Mesa de partes digital - I.E. N.° 81770 "María Inmaculada Concepción" (Chao, Virú)

Prototipo de consola en **Python 3** para el curso **Fundamentos de Programación (CIIN1205P)**, UPN - Grupo 3.
Reto: "Del archivador al algoritmo". Solución elegida: **Alternativa B** (sistema modular con arreglos paralelos en memoria).

## Ejecución
```
python mesa_de_partes.py
```
Requiere Python 3.8 o superior. No usa librerías externas.
Códigos de acceso de prueba: `SEC-01` y `SEC-02` (secretarias), `DIR-01` (director) (3 intentos).

## Menú
| Opción | Función |
|---|---|
| 1 | Registrar solicitud: primero la condición (estudiante o egresado), luego DNI, apellidos, nombres y celular. El estudiante indica nivel y el grado que cursa; el egresado no tiene nivel y pasa directo a su edad. Después el trámite (el egresado solo ve constancia de estudios, certificado de estudios, actualización de datos y otros) y los folios. **Antes de guardar se muestra un resumen y se pide confirmar (S/N)**. Fecha y hora las toma el sistema; estado inicial Registrado; se guarda quién registró |
| 2 | Buscar eligiendo el campo (código, DNI, apellidos y nombres, grado o edad, condición, trámite o estado). Los resultados salen en una tabla |
| 3 | Ordenar por código, fecha, nombre, nivel o trámite (ascendente o descendente). Se muestra como una tabla tipo Excel (una fila por solicitud, columnas alineadas); si la consola es angosta se recortan los textos largos y se ocultan celular y responsable |
| 4 | Reporte de documentos (por trámite y estado) |
| 5 | Lista de trámites; permite abrir un expediente (remitente, DNI, estado y su historial de seguimiento) |
| 6 | Actualizar estado (pide siempre el motivo): Registrado → En revisión → Observado → Aprobado / Rechazado. Las secretarias pueden pasar una solicitud a **En revisión** y a **Observado**; **solo el director (`DIR-01`) ve y puede elegir Aprobado o Rechazado**. Antes de aprobar o rechazar se pide confirmar (S/N) y el rechazo exige un motivo claro (mínimo 10 caracteres). Aprobado y Rechazado son finales |
| 0 | Salir |

## Permisos por cargo
| Cargo | Qué ve y puede hacer |
|---|---|
| Secretaria (`SEC-01`, `SEC-02`) | Solo ve (buscar, ordenar, reporte, lista, expediente) y actualiza las solicitudes que ella registró. Puede pasarlas de Registrado a En revisión y de En revisión a Observado |
| Director (`DIR-01`) | Ve todas las solicitudes. Es el único que aprueba o rechaza |

Las solicitudes antiguas sin registrador (líneas de 8 campos) las ve solo el director.

## Archivos de texto
Se crean junto al programa, con los campos separados por `|`. Los campos vacíos se guardan con `-`.

`Tramite.txt` (14 campos, una línea por solicitud):
`codigo|fecha|hora|n.° de trámite de la persona|dni|apellidos|nombres|celular|condicion|nivel|grado o edad|tipo de trámite|folios|registrador`
```
SOL-001|20-11-26|22:40|1|74125896|Paredes Lozano|Valeria Camila|987123456|ESTUDIANTE|SECUNDARIA|4|CONSTANCIA DE ESTUDIOS|2|SEC-01
SOL-002|20-11-26|22:41|1|46281937|Mendoza Quiroz|Rosa Elena|932415680|EGRESADO|-|24|CERTIFICADO DE ESTUDIOS|3|SEC-01
```
- `n.° de trámite de la persona`: cuántos trámites lleva registrados esa persona (mismo DNI): 1 el primero, 2 el segundo, etc.
- `registrador`: código de acceso de quien registró (SEC-01, SEC-02 o DIR-01).
- El egresado no tiene nivel (`-`) y en `grado o edad` va su edad.

`Seguimiento.txt` (una línea por cada cambio de estado):
`numero|fase|fecha|hora|motivo|responsable`
```
1|Registrado|20-11-26|22:40|Solicitud registrada|SEC-01
1|En revision|20-11-26|23:05|Documentos completos|SEC-02
1|Observado|20-11-26|23:10|Falta copia del DNI|SEC-02
1|Aprobado|21-11-26|08:30|Presento el DNI|DIR-01
```
(`numero` es el número del código: SOL-001 → 1; `responsable` es quien hizo el cambio.)

Al abrir el programa se vuelven a cargar todos los datos. También se leen los formatos antiguos de `Tramite.txt` (8 y 9 campos) y de `Seguimiento.txt` (5 campos).

## Pruebas
```
python -m unittest -v
```

## Historial
Cada observación del docente se resolvió en un commit propio: ver `git log --oneline`.

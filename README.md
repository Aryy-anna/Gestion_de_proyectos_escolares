# Mesa de partes digital - I.E. N.° 81770 "María Inmaculada Concepción" (Chao, Virú)

Prototipo de consola en **Python 3** para el curso **Fundamentos de Programación (CIIN1205P)**, UPN - Grupo 3.
Reto: "Del archivador al algoritmo". Solución elegida: **Alternativa B** (sistema modular con arreglos paralelos en memoria).

## Ejecución
```
python mesa_de_partes.py
```
Requiere Python 3.8 o superior. No usa librerías externas.
Códigos de acceso de prueba: `SEC-01`, `SEC-02`, `DIR-01` (3 intentos).

## Menú
| Opción | Función |
|---|---|
| 1 | Registrar solicitud (condición estudiante o egresado; la fecha la toma el sistema; estado inicial RECIBIDO) |
| 2 | Buscar por código, DNI, nombre, grado, condición o trámite (búsqueda lineal) |
| 3 | Ordenar por código, fecha, nombre, nivel o trámite (burbuja o inserción) |
| 4 | Reporte por trámite y estado |
| 5 | Mostrar todas las solicitudes |
| 6 | Actualizar estado: RECIBIDO, EN REVISION, OBSERVADO o ATENDIDO (APROBADO o RECHAZADO), con nota de observación |
| 7 | Reporte de documentos (solicitados, en trámite, aprobados, rechazados) |
| 8 | Índice de ingresos por fecha |
| 0 | Salir |

Los datos viven en memoria mientras el programa está abierto; guardarlos en archivo queda como mejora (Alternativa A).

## Pruebas
```
python -m unittest -v
```

## Historial
Cada observación del docente se resolvió en un commit propio: ver `git log --oneline`.

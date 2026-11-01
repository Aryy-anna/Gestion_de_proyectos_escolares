# Mesa de partes digital - I.E. N.° 81770 "María Inmaculada Concepción" (Chao, Virú)

Prototipo de consola en **Python** para el curso **Fundamentos de Programación (CIIN1205P)**, UPN - Grupo 3.
Reto: "Del archivador al algoritmo". Solución elegida: **Alternativa B** (sistema simplificado con acceso y búsqueda por código).

## Ejecución
```
python mesa_de_partes.py
```
Requiere Python 3.8 o superior. No usa librerías externas. Códigos de acceso de prueba: `SEC-01`, `SEC-02`.

## Funciones del menú
| Opción | Función |
|---|---|
| 1 | Registrar solicitud (condición estudiante/egresado, fecha del sistema, estado inicial RECIBIDO) |
| 2 | Buscar solicitud por código (búsqueda secuencial) |
| 3 | Actualizar estado: RECIBIDO > EN REVISIÓN > OBSERVADO / APROBADO / RECHAZADO > ATENDIDO, con nota de observación |
| 4 | Ordenar por código (inserción, ascendente o descendente) |
| 5 | Reporte de documentos (matriz trámite × estado y detalle por trámite) |
| 6 | Índice de ingresos (orden de llegada y conteo por fecha) |
| 7 | Mostrar todas las solicitudes |

Los datos se guardan en `solicitudes.csv` (separador `;`).

## Pruebas
```
python -m unittest -v test_mesa_de_partes
```

## Historial
Cada observación del docente se resolvió en un commit propio: ver `git log --oneline`.

# Sistema de Control Escolar (tipo SIIAU) — Hito 2

Proyecto integrador de **Programación II** (CUGDL, ciclo 2026B), opción A.

**Integrantes**

- Aldo Dariel González González (225996542)
- Ángel Zaid Cervantes Ruvalcaba (225361997)

## Qué hace

Registra **alumnos**, **docentes** y **materias**, e inscribe a una persona en una
materia mientras queden lugares. Rechaza cualquier dato inválido con una excepción
que explica el motivo, anota en una bitácora lo que va pasando y guarda todo en un
archivo JSON para recuperarlo la próxima vez que se abra el programa.

## Cómo se ejecuta

Requiere Python 3.10 o más reciente; no usa bibliotecas externas.

```bash
python main.py
```

- La primera vez no existe el archivo de datos: el programa arranca vacío, registra
  datos de ejemplo (inventados), intenta varias operaciones inválidas y guarda en
  `datos_escolares.json`.
- Si lo ejecutan otra vez, recupera la información del archivo.
- Si borran o dañan `datos_escolares.json`, el programa avisa y vuelve a arrancar vacío.

## Archivos

| Archivo | De qué se encarga |
| --- | --- |
| `validacion.py` | Excepciones propias (`ValidacionException`, `CodigoDuplicadoException`, `CupoExcedidoException`) y la clase `Validador` |
| `modelo.py` | Jerarquía `Persona` → `Alumno` / `Docente`, más la clase `Materia` (contenedor con cupo) |
| `sistema.py` | `Repositorio` (colecciones en memoria) y `ControlEscolar` (clase principal del contrato) |
| `almacen.py` | `Bitacora` y las funciones `guardar(sistema, ruta)` / `cargar(sistema, ruta)` |
| `main.py` | Programa de demostración que se ejecuta |

## El contrato

```python
from modelo import Alumno, Docente, Materia
from sistema import ControlEscolar
from almacen import guardar, cargar

sistema = ControlEscolar()
cargar(sistema, "datos.json")            # si no existe, arranca vacío

sistema.registrar(Alumno("219000001", "Mariana Torres", "Ciberseguridad"))
sistema.registrar(Docente("100000001", "Roberto Medina", "Ciencias Computacionales"))
sistema.registrar(Materia("IL352", "Programación II", 30))

sistema.asignar("219000001", "IL352")    # inscribe por código y clave
sistema.listar()                          # imprime cada registro con su formato
guardar(sistema, "datos.json")
```

`guardar` y `cargar` también pueden llamarse como `ControlEscolar.guardar(sistema, ruta)`
o `sistema.guardar(sistema, ruta)`; las tres formas hacen lo mismo. Ninguno de los cinco
métodos usa `input()`.

## Validaciones

Todas las excepciones del sistema heredan de `ValidacionException`, que a su vez
hereda de `ValueError`, así que basta con `except ValueError` para capturarlas.

| Si se intenta… | Resultado |
| --- | --- |
| Registrar una persona con nombre vacío o de puros espacios | `ValidacionException`: el nombre es obligatorio |
| Registrar un código vacío o que no tenga exactamente 9 dígitos | `ValidacionException`: pide 9 dígitos numéricos |
| Registrar un alumno sin carrera o un docente sin departamento | `ValidacionException`: indica qué campo falta |
| Registrar un código que ya existe | `CodigoDuplicadoException` |
| Registrar algo que no es Alumno, Docente ni Materia | `ValidacionException`: indica qué se esperaba |
| Crear una materia sin clave, sin nombre o con cupo no entero o ≤ 0 | `ValidacionException`: indica el campo o pide cupo mayor que cero |
| Registrar una materia con una clave ya usada | `CodigoDuplicadoException` |
| Inscribir a una persona no registrada | `ValidacionException`: pide darla de alta primero |
| Inscribir en una materia que no existe | `ValidacionException` |
| Inscribir dos veces a la misma persona en la misma materia | `ValidacionException`: ya está inscrita |
| Inscribir en una materia llena | `CupoExcedidoException` |
| Abrir el programa sin archivo de datos | Arranca vacío, sin error |
| Abrir un archivo dañado o con datos inválidos | Avisa del problema y arranca vacío |

Las claves de materia no distinguen mayúsculas de minúsculas (`il352` = `IL352`).

## Cómo se aplican los conceptos

- **Herencia:** `Alumno` y `Docente` heredan de `Persona` (clase abstracta).
- **Polimorfismo:** `describir()` se redefine en cada tipo y extiende la versión base con
  `super()`. `listar()` solo le pide a cada registro que se describa, sin preguntar su tipo.
- **Composición:** `ControlEscolar` *tiene un* `Repositorio` y *tiene una* `Bitacora`, y le
  delega a esta el registro de cada alta, inscripción o rechazo.
- **Encapsulamiento:** todos los atributos internos llevan guion bajo y se exponen con
  propiedades de solo lectura (`codigo`, `nombre`, `carrera`, `clave`, `inscritos`, …).
  Ninguna clase toca los atributos internos de otra; la persistencia usa `a_dict()` y
  `desde_dict()`.

## Cambios respecto al Hito 1

En el diagrama del Hito 1 usamos nombres al estilo Java (`registrarAlumno`, `inscribir`,
`getCodigo()`); al programar los cambiamos a los nombres del contrato (`registrar`,
`asignar`, `listar`) y a propiedades de Python, siguiendo PEP 8. Como el contrato solo
tiene un método de alta, `registrar(objeto)` acepta también objetos `Materia`
(además existe `crear_materia(materia)`, que solo acepta materias); por eso el mensaje
de "objeto no válido" menciona alumno, docente o materia. Hicimos que
`ValidacionException` herede de `ValueError` para cumplir con la forma estándar de
rechazar datos vista en clase. Agregamos la clase `Bitacora`, que no estaba en el
diagrama, para cumplir el requisito de composición, y elegimos JSON como formato de
archivo porque permite guardar el tipo de cada persona y reconstruirla con su clase.

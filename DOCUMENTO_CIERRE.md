# Documento de Cierre — Proyecto Integrador

**Materia:** Programación II · Ciclo 2026B · CUGDL (Universidad de Guadalajara)  
**Docente:** Martha Ulloa Ramírez  
**Proyecto:** Sistema de Control Escolar (Opción A, tipo SIIAU)  
**Integrantes:** Aldo Dariel González González (`225996542`) y Ángel Zaid Cervantes Ruvalcaba (`225361997`)  
**Repositorio:** `progii-2026b-gonzalez-cervantes`

---

## 1. Qué cambió del Hito 1 al final y por qué

Al trasladar el diseño del Hito 1 a código Python realizamos ajustes puntuales para alinear el diagrama con el contrato del proyecto y las buenas prácticas del lenguaje. En primer lugar, renombramos los métodos que en el diagrama inicial aparecían con estilo Java (`registrarAlumno`, `inscribir`, `getCodigo()`, `getTipo()`) para usar exactamente los nombres del contrato (`registrar`, `asignar`, `listar`, `guardar`, `cargar`) junto con propiedades `@property` de solo lectura siguiendo PEP 8.

En segundo lugar, dado que el contrato solo contempla un método de alta (`registrar(objeto)`), decidimos que también acepte objetos `Materia` además de `Alumno` y `Docente` (manteniendo `crear_materia` como método específico), de modo que el sistema completo pueda operarse únicamente con los cinco métodos fijos. También hicimos que nuestra excepción base `ValidacionException` herede de `ValueError` para conservar la claridad de `CodigoDuplicadoException` y `CupoExcedidoException` sin perder compatibilidad con capturas estándar `except ValueError`.

Por último, añadimos la clase `Bitacora` para materializar la relación de composición con `ControlEscolar`, implementamos persistencia en JSON mediante `a_dict()` y `desde_dict()` para respetar el encapsulamiento, agregamos una suite de 12 pruebas automáticas en `pruebas.py` y sumamos una interfaz web local opcional en `servidor.py` usando únicamente la biblioteca estándar de Python.

## 2. Qué fue lo más difícil

El reto técnico principal fue blindar todas las entradas y la persistencia para que ningún dato mal formado tumbara el programa. En Python, por ejemplo, `bool` hereda de `int`, por lo que validar códigos y cupos exigió filtrar explícitamente booleanos, cadenas vacías, espacios y valores `None` antes de operar con ellos. En la carga desde JSON también fue necesario contemplar no solo la ausencia del archivo o errores de sintaxis, sino archivos con estructura válida pero datos alterados manualmente.

A nivel de diseño, lo más exigente fue sostener el bajo acoplamiento y el polimorfismo sin atajos: evitar que la persistencia o la interfaz web accedieran directamente a atributos privados (`_`) y asegurar que `listar()` delegara el formato a `describir()` con `super()` sin preguntar tipos. En la colaboración por Git, coordinar las entregas incrementales y fusionar ramas nuevas sin pisar cambios previos requirió disciplina constante con `fetch`, `pull` y mensajes claros.

## 3. Qué haríamos distinto

Si volviéramos a iniciar el proyecto, definiríamos desde el diagrama del Hito 1 los nombres exactos de Python y del contrato, incluiríamos desde el primer boceto la `Bitacora` y los métodos de serialización, y planificaríamos en paralelo la escritura de `pruebas.py` conforme se desarrolla cada clase. Automatizar los casos límite desde el primer día habría detectado antes detalles sutiles de validación y habría reducido el esfuerzo de verificación antes del cierre.

# Guía de Ejecución y Acceso al Sistema

Este documento detalla las instrucciones para ejecutar el **Sistema de Control Escolar** en un entorno local, así como la información de acceso para el servicio alojado en la nube.

---

## 1. Ejecución en Entorno Local

### Requisitos previos
* **Python 3.10** o superior instalado en el equipo.
* No se requieren bibliotecas externas (`pip`); el proyecto utiliza únicamente la biblioteca estándar de Python.

### Pasos de ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Aldini057/progii-2026b-gonzalez-cervantes.git
   cd progii-2026b-gonzalez-cervantes
   ```

2. **Ejecutar el programa de demostración (Línea de comandos):**
   ```bash
   python main.py
   ```
   * En la primera ejecución se inicializa sin datos previos, genera registros de prueba, evalúa los casos de validación y guarda el estado en `datos_escolares.json`.
   * En ejecuciones posteriores, recupera automáticamente los datos existentes desde el archivo JSON.

3. **Ejecutar la interfaz web / servidor local (Rama `interfas-grafica`):**
   Si se cuenta con la interfaz gráfica integrada en el proyecto:
   ```bash
   python servidor.py
   ```
   * Abre en cualquier navegador web:
     * [http://localhost:8000](http://localhost:8000)
     * [http://127.0.0.1:8000](http://127.0.0.1:8000)
   * Permite gestionar altas de alumnos, docentes y materias, realizar inscripciones y consultar la bitácora de eventos en tiempo real.

---

## 2. Servicio Desplegado en la Nube

El sistema se encuentra desplegado y accesible públicamente a través del siguiente dominio:

* **URL del servicio:** [https://siuu.crew-lab.com](https://siuu.crew-lab.com)

### Políticas de Autenticación y Control de Acceso

El acceso al servicio está protegido mediante inicio de sesión federado exclusivo para la comunidad de la **Universidad de Guadalajara (UdeG)**.

El sistema de autenticación restringe el acceso bajo la regla:
> **Include → Emails ending in:**
> * `@udg.mx`
> * `@academicos.udg.mx` *(utilizado normalmente por profesores y personal académico)*
> * `@alumnos.udg.mx` *(utilizado por alumnos y estudiantes)*

Cualquier dirección de correo que no pertenezca a alguno de estos tres dominios institucionales será rechazada automáticamente.

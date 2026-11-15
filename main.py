"""Programa de demostración: carga, opera, intenta datos inválidos y guarda."""

import os

from almacen import cargar, guardar
from modelo import Alumno, Docente, Materia
from sistema import ControlEscolar

RUTA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_escolares.json")


def intentar(descripcion, operacion):
    """Ejecuta una operación y muestra si se aceptó o el motivo del rechazo."""
    try:
        operacion()
        print(f"  [ACEPTADO]  {descripcion}")
    except ValueError as error:
        print(f"  [RECHAZADO] {descripcion}\n              -> {error}")


def registrar_datos_de_ejemplo(sistema):
    """Da de alta personas y materias inventadas para la primera ejecución."""
    for objeto in (
        Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"),
        Alumno("219000002", "Luis Ramírez Soto", "Ciberseguridad"),
        Alumno("219000003", "Sofía Herrera Luna", "Informática"),
        Docente("100000001", "Roberto Medina Ríos", "Ciencias Computacionales"),
        Materia("IL352", "Programación II", 2),
        Materia("IL360", "Redes de Computadoras", 30),
    ):
        sistema.registrar(objeto)
    sistema.asignar("219000001", "IL352")
    sistema.asignar("219000002", "IL352")
    sistema.asignar("100000001", "IL360")


def probar_rechazos(sistema):
    """Intenta operaciones inválidas; todas deben rechazarse sin tumbar el programa."""
    intentar("Alumno con código de 8 dígitos",
             lambda: sistema.registrar(Alumno("12345678", "Pedro Gómez", "Informática")))
    intentar("Alumno con letras en el código",
             lambda: sistema.registrar(Alumno("21900A001", "Pedro Gómez", "Informática")))
    intentar("Alumno con nombre de puros espacios",
             lambda: sistema.registrar(Alumno("219000009", "   ", "Informática")))
    intentar("Alumno sin carrera",
             lambda: sistema.registrar(Alumno("219000009", "Pedro Gómez", "")))
    intentar("Docente sin departamento",
             lambda: sistema.registrar(Docente("100000009", "Ana Ruiz", None)))
    intentar("Código repetido",
             lambda: sistema.registrar(Docente("219000001", "Otra Persona", "Matemáticas")))
    intentar("Registrar algo que no es alumno, docente ni materia",
             lambda: sistema.registrar("219000010"))
    intentar("Materia con cupo cero",
             lambda: sistema.registrar(Materia("IL999", "Materia Fantasma", 0)))
    intentar("Materia con cupo no numérico",
             lambda: sistema.registrar(Materia("IL999", "Materia Fantasma", "diez")))
    intentar("Materia con clave repetida",
             lambda: sistema.registrar(Materia("il352", "Otra Programación", 10)))
    intentar("Inscribir a alguien no registrado",
             lambda: sistema.asignar("299999999", "IL360"))
    intentar("Inscribir en una materia que no existe",
             lambda: sistema.asignar("219000003", "XX000"))
    intentar("Inscribir dos veces a la misma persona",
             lambda: sistema.asignar("219000001", "IL352"))
    intentar("Inscribir en una materia llena",
             lambda: sistema.asignar("219000003", "IL352"))


def main():
    """Punto de entrada del programa."""
    sistema = ControlEscolar()
    if cargar(sistema, RUTA_DATOS):
        print(f"Datos recuperados de {RUTA_DATOS}\n")
    else:
        print("Sin datos previos: se registran datos de ejemplo.\n")
        registrar_datos_de_ejemplo(sistema)

    sistema.listar()
    print("\nIntentos con datos inválidos:")
    probar_rechazos(sistema)

    guardar(sistema, RUTA_DATOS)
    print(f"\nEstado guardado en {RUTA_DATOS}")
    print("Vuelve a ejecutar el programa para comprobar que la información sigue ahí.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # Última red de seguridad: nunca terminar con un traceback.
        print(f"Error inesperado: {type(error).__name__}: {error}")

"""Bitácora de eventos y persistencia del sistema en un archivo JSON."""

import json
import os
from datetime import datetime

from modelo import Alumno, Docente, Materia

TIPOS_PERSONA = {"Alumno": Alumno, "Docente": Docente}
ERRORES_DE_ARCHIVO = (OSError, ValueError, KeyError, TypeError, AttributeError)


class Bitacora:
    """Registra en orden los eventos que ocurren en el sistema."""

    def __init__(self):
        """Crea la bitácora sin eventos."""
        self._eventos = []

    @property
    def eventos(self):
        """Eventos registrados, como tupla de solo lectura."""
        return tuple(self._eventos)

    def anotar(self, mensaje):
        """Agrega un evento con la fecha y hora actuales."""
        self._eventos.append(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {mensaje}")

    def restaurar(self, eventos):
        """Reemplaza los eventos por los que se recuperaron del archivo."""
        if not isinstance(eventos, list):
            raise TypeError("la bitácora guardada debe ser una lista")
        self._eventos = [str(evento) for evento in eventos]

    def mostrar(self):
        """Imprime todos los eventos en orden."""
        for evento in self._eventos:
            print(evento)

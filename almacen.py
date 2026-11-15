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


def _validar_ruta(ruta):
    """Devuelve la ruta como texto o lanza ValueError si no es válida."""
    if not isinstance(ruta, (str, os.PathLike)) or not str(ruta).strip():
        raise ValueError("La ruta del archivo de datos es obligatoria.")
    return os.fspath(ruta)


def guardar(sistema, ruta):
    """Escribe el estado completo del sistema en un archivo JSON.

    Primero escribe en un archivo temporal y luego lo reemplaza, para no
    dejar un archivo a medias si algo falla. Lanza ValueError si no se
    puede escribir.
    """
    ruta = _validar_ruta(ruta)
    datos = {
        "personas": [persona.a_dict() for persona in sistema.personas()],
        "materias": [materia.a_dict() for materia in sistema.materias()],
        "bitacora": list(sistema.bitacora.eventos),
    }
    temporal = ruta + ".tmp"
    try:
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        os.replace(temporal, ruta)
    except OSError as error:
        raise ValueError(f"No se pudo guardar en '{ruta}': {error}") from error
    sistema.bitacora.anotar(f"Datos guardados en {os.path.basename(ruta)}")


def cargar(sistema, ruta):
    """Lee el archivo JSON y reconstruye el estado del sistema.

    Si el archivo no existe, el sistema queda vacío sin error. Si está
    dañado o tiene datos inválidos, avisa y también arranca vacío.
    Devuelve True si se recuperaron datos y False si se inició vacío.
    """
    ruta = _validar_ruta(ruta)
    sistema.reiniciar()
    if not os.path.exists(ruta):
        sistema.bitacora.anotar("No existe archivo de datos: se inicia vacío")
        return False
    try:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        for registro in datos["personas"]:
            sistema.registrar(TIPOS_PERSONA[registro["tipo"]].desde_dict(registro))
        for registro in datos["materias"]:
            sistema.registrar(Materia.desde_dict(registro))
        for registro in datos["materias"]:
            for codigo in registro["inscritos"]:
                sistema.asignar(codigo, registro["clave"])
        sistema.bitacora.restaurar(datos.get("bitacora", []))
    except ERRORES_DE_ARCHIVO as error:
        print(f"Aviso: el archivo '{ruta}' está dañado o tiene un formato inválido "
              f"({type(error).__name__}: {error}). Se inicia con los registros vacíos.")
        sistema.reiniciar()
        sistema.bitacora.anotar("Archivo de datos dañado: se inicia vacío")
        return False
    sistema.bitacora.anotar(f"Datos cargados desde {os.path.basename(ruta)}")
    return True

"""Excepciones propias del sistema y reglas para revisar los datos de entrada."""

import re


class ValidacionException(ValueError):
    """Error base para cualquier regla del control escolar que no se cumple.

    Hereda de ValueError para que también pueda capturarse como el error
    estándar de Python para datos inválidos.
    """


class CodigoDuplicadoException(ValidacionException):
    """Error que se lanza al registrar un código o una clave que ya existe."""


class CupoExcedidoException(ValidacionException):
    """Error que se lanza al inscribir a alguien en una materia llena."""

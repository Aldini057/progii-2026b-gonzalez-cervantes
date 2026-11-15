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


class Validador:
    """Revisa los datos de entrada antes de que se usen en una operación."""

    _PATRON_CODIGO = re.compile(r"[0-9]{9}")

    @staticmethod
    def texto_obligatorio(valor, campo):
        """Devuelve el texto sin espacios en los extremos.

        Lanza ValidacionException si el valor no es texto, está vacío o
        solo contiene espacios.
        """
        if valor is not None and not isinstance(valor, str):
            raise ValidacionException(
                f"El campo '{campo}' debe ser texto, se recibió {type(valor).__name__}."
            )
        if valor is None or not valor.strip():
            raise ValidacionException(
                f"El campo '{campo}' es obligatorio y no puede ir vacío."
            )
        return valor.strip()

    @classmethod
    def codigo(cls, valor):
        """Devuelve el código como texto si tiene exactamente nueve dígitos.

        Acepta texto o entero; cualquier otro caso lanza ValidacionException.
        """
        if isinstance(valor, int) and not isinstance(valor, bool):
            valor = str(valor)
        if not isinstance(valor, str) or not cls._PATRON_CODIGO.fullmatch(valor.strip()):
            raise ValidacionException(
                f"Código inválido ({valor!r}): debe tener exactamente 9 dígitos numéricos."
            )
        return valor.strip()

    @staticmethod
    def clave(valor):
        """Devuelve la clave de materia en mayúsculas si no viene vacía."""
        return Validador.texto_obligatorio(valor, "clave de la materia").upper()

    @staticmethod
    def cupo(valor):
        """Devuelve el cupo si es un número entero mayor que cero."""
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValidacionException(
                f"El cupo debe ser un número entero, se recibió {valor!r}."
            )
        if valor <= 0:
            raise ValidacionException(
                f"El cupo debe ser mayor que cero, se recibió {valor}."
            )
        return valor

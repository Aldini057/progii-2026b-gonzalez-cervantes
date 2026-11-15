"""Clase principal del control escolar con las operaciones del contrato."""

from validacion import CodigoDuplicadoException, ValidacionException


class Repositorio:
    """Mantiene en memoria las personas y materias registradas."""

    def __init__(self):
        """Crea las colecciones vacías, indexadas por código y por clave."""
        self._personas = {}
        self._materias = {}

    def agregar_persona(self, persona):
        """Guarda una persona si su código no está repetido."""
        if persona.codigo in self._personas:
            raise CodigoDuplicadoException(f"El código {persona.codigo} ya está registrado.")
        self._personas[persona.codigo] = persona

    def agregar_materia(self, materia):
        """Guarda una materia si su clave no está repetida."""
        if materia.clave in self._materias:
            raise CodigoDuplicadoException(f"La clave de materia {materia.clave} ya está registrada.")
        self._materias[materia.clave] = materia

    def buscar_persona(self, codigo):
        """Devuelve la persona con ese código o lanza error si no existe."""
        if codigo not in self._personas:
            raise ValidacionException(
                f"No hay ninguna persona registrada con el código {codigo}; "
                "primero hay que darla de alta."
            )
        return self._personas[codigo]

    def buscar_materia(self, clave):
        """Devuelve la materia con esa clave o lanza error si no existe."""
        if clave not in self._materias:
            raise ValidacionException(f"No hay una materia registrada con la clave {clave}.")
        return self._materias[clave]

    def personas(self):
        """Devuelve la lista de personas en orden de registro."""
        return list(self._personas.values())

    def materias(self):
        """Devuelve la lista de materias en orden de registro."""
        return list(self._materias.values())

    def vaciar(self):
        """Elimina todos los registros."""
        self._personas.clear()
        self._materias.clear()

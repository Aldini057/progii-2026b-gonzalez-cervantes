"""Clase principal del control escolar con las operaciones del contrato."""

import almacen
from almacen import Bitacora
from modelo import Materia, Persona
from validacion import CodigoDuplicadoException, ValidacionException, Validador


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


class ControlEscolar:
    """Coordina las operaciones del control escolar."""

    def __init__(self):
        """Crea el sistema vacío; tiene un repositorio y una bitácora propios."""
        self._repositorio = Repositorio()
        self._bitacora = Bitacora()

    @property
    def bitacora(self):
        """Bitácora donde el sistema anota lo que va pasando (solo lectura)."""
        return self._bitacora

    def registrar(self, objeto):
        """Da de alta un Alumno, un Docente o una Materia ya construidos.

        Lanza CodigoDuplicadoException si el código o la clave ya existen y
        ValidacionException si el objeto no es de un tipo que se pueda registrar.
        """
        try:
            if isinstance(objeto, Persona):
                self._repositorio.agregar_persona(objeto)
            elif isinstance(objeto, Materia):
                self._repositorio.agregar_materia(objeto)
            else:
                raise ValidacionException(
                    "Se esperaba un Alumno, un Docente o una Materia válidos, "
                    f"pero se recibió {type(objeto).__name__}."
                )
        except ValidacionException as error:
            self._bitacora.anotar(f"Registro rechazado: {error}")
            raise
        self._bitacora.anotar(f"Alta: {objeto.describir()}")

    def crear_materia(self, materia):
        """Da de alta una materia; equivale a registrar(materia) pero solo acepta materias."""
        if not isinstance(materia, Materia):
            raise ValidacionException("Se esperaba un objeto Materia.")
        self.registrar(materia)

    def asignar(self, identificador, clave):
        """Inscribe a la persona con ese código en la materia con esa clave.

        Lanza ValidacionException si el código o la clave son inválidos, si
        la persona o la materia no existen o si ya estaba inscrita, y
        CupoExcedidoException si la materia está llena.
        """
        try:
            codigo = Validador.codigo(identificador)
            clave = Validador.clave(clave)
            persona = self._repositorio.buscar_persona(codigo)
            materia = self._repositorio.buscar_materia(clave)
            materia.inscribir(persona.codigo)
        except ValidacionException as error:
            self._bitacora.anotar(f"Inscripción rechazada: {error}")
            raise
        self._bitacora.anotar(f"Inscripción: {persona.codigo} en {materia.clave}")

    def listar(self):
        """Imprime todos los registros; cada uno se describe con su propio formato."""
        secciones = (("PERSONAS", self._repositorio.personas()),
                     ("MATERIAS", self._repositorio.materias()))
        for titulo, registros in secciones:
            print(f"--- {titulo} ({len(registros)}) ---")
            for registro in registros:
                print(registro.describir())

    def personas(self):
        """Devuelve la lista de personas registradas."""
        return self._repositorio.personas()

    def materias(self):
        """Devuelve la lista de materias registradas."""
        return self._repositorio.materias()

    def reiniciar(self):
        """Deja el sistema sin registros (la bitácora se conserva)."""
        self._repositorio.vaciar()

    @staticmethod
    def guardar(sistema, ruta):
        """Escribe el estado del sistema en la ruta indicada (delega en almacen)."""
        almacen.guardar(sistema, ruta)

    @staticmethod
    def cargar(sistema, ruta):
        """Reconstruye el sistema desde la ruta indicada (delega en almacen)."""
        return almacen.cargar(sistema, ruta)

"""Clases que representan a las personas y a las materias del control escolar."""

from abc import ABC, abstractmethod

from validacion import CupoExcedidoException, ValidacionException, Validador


class Persona(ABC):
    """Reúne los datos comunes de cualquier persona registrada."""

    def __init__(self, codigo, nombre):
        """Valida y guarda el código de 9 dígitos y el nombre."""
        self._codigo = Validador.codigo(codigo)
        self._nombre = Validador.texto_obligatorio(nombre, "nombre")

    @property
    def codigo(self):
        """Código de 9 dígitos de la persona (solo lectura)."""
        return self._codigo

    @property
    def nombre(self):
        """Nombre completo de la persona (solo lectura)."""
        return self._nombre

    @property
    def tipo(self):
        """Nombre del tipo concreto de persona (Alumno o Docente)."""
        return type(self).__name__

    @abstractmethod
    def describir(self):
        """Devuelve la parte común de la descripción; cada tipo la extiende."""
        return f"[{self.codigo}] {self.nombre}"

    def a_dict(self):
        """Devuelve los datos comunes listos para guardarse en el archivo."""
        return {"tipo": self.tipo, "codigo": self.codigo, "nombre": self.nombre}


class Alumno(Persona):
    """Representa a un estudiante inscrito en una carrera."""

    def __init__(self, codigo, nombre, carrera):
        """Valida los datos comunes y la carrera del alumno."""
        super().__init__(codigo, nombre)
        self._carrera = Validador.texto_obligatorio(carrera, "carrera")

    @property
    def carrera(self):
        """Carrera que cursa el alumno (solo lectura)."""
        return self._carrera

    def describir(self):
        """Extiende la descripción común con la carrera."""
        return f"Alumno   {super().describir()} | Carrera: {self.carrera}"

    def a_dict(self):
        """Agrega la carrera a los datos comunes."""
        datos = super().a_dict()
        datos["carrera"] = self.carrera
        return datos

    @classmethod
    def desde_dict(cls, datos):
        """Reconstruye un alumno a partir de los datos guardados."""
        return cls(datos["codigo"], datos["nombre"], datos["carrera"])


class Docente(Persona):
    """Representa a un profesor adscrito a un departamento."""

    def __init__(self, codigo, nombre, departamento):
        """Valida los datos comunes y el departamento del docente."""
        super().__init__(codigo, nombre)
        self._departamento = Validador.texto_obligatorio(departamento, "departamento")

    @property
    def departamento(self):
        """Departamento al que pertenece el docente (solo lectura)."""
        return self._departamento

    def describir(self):
        """Extiende la descripción común con el departamento."""
        return f"Docente  {super().describir()} | Departamento: {self.departamento}"

    def a_dict(self):
        """Agrega el departamento a los datos comunes."""
        datos = super().a_dict()
        datos["departamento"] = self.departamento
        return datos

    @classmethod
    def desde_dict(cls, datos):
        """Reconstruye un docente a partir de los datos guardados."""
        return cls(datos["codigo"], datos["nombre"], datos["departamento"])


class Materia:
    """Lleva el registro de inscritos dentro de un cupo máximo."""

    def __init__(self, clave, nombre, cupo_maximo):
        """Valida la clave, el nombre y el cupo; empieza sin inscritos."""
        self._clave = Validador.clave(clave)
        self._nombre = Validador.texto_obligatorio(nombre, "nombre de la materia")
        self._cupo_maximo = Validador.cupo(cupo_maximo)
        self._inscritos = []

    @property
    def clave(self):
        """Clave única de la materia (solo lectura)."""
        return self._clave

    @property
    def nombre(self):
        """Nombre de la materia (solo lectura)."""
        return self._nombre

    @property
    def cupo_maximo(self):
        """Número máximo de inscritos (solo lectura)."""
        return self._cupo_maximo

    @property
    def inscritos(self):
        """Códigos inscritos, como tupla para que no se modifiquen desde fuera."""
        return tuple(self._inscritos)

    @property
    def lugares_disponibles(self):
        """Lugares que todavía quedan en la materia."""
        return self._cupo_maximo - len(self._inscritos)

    def esta_inscrito(self, codigo):
        """Indica si el código ya está inscrito en la materia."""
        return codigo in self._inscritos

    def inscribir(self, codigo):
        """Inscribe un código si no está repetido y queda lugar."""
        if self.esta_inscrito(codigo):
            raise ValidacionException(
                f"La persona {codigo} ya está inscrita en la materia {self.clave}."
            )
        if self.lugares_disponibles <= 0:
            raise CupoExcedidoException(
                f"La materia {self.clave} ya alcanzó su cupo máximo ({self.cupo_maximo})."
            )
        self._inscritos.append(codigo)

    def describir(self):
        """Devuelve una línea con los datos de la materia y sus inscritos."""
        lista = ", ".join(self._inscritos) or "ninguno"
        return (f"Materia  [{self.clave}] {self.nombre} | "
                f"Cupo: {len(self._inscritos)}/{self.cupo_maximo} | Inscritos: {lista}")

    def a_dict(self):
        """Devuelve los datos de la materia listos para guardarse."""
        return {"clave": self.clave, "nombre": self.nombre,
                "cupo_maximo": self.cupo_maximo, "inscritos": list(self._inscritos)}

    @classmethod
    def desde_dict(cls, datos):
        """Reconstruye la materia vacía; los inscritos se vuelven a asignar al cargar."""
        return cls(datos["clave"], datos["nombre"], datos["cupo_maximo"])

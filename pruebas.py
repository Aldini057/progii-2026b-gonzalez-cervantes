"""Suite de pruebas automáticas para el Sistema de Control Escolar."""

from contextlib import redirect_stdout
import io
import json
import os
import tempfile
import unittest

from almacen import cargar, guardar
from modelo import Alumno, Docente, Materia
from sistema import ControlEscolar
from validacion import (
    CodigoDuplicadoException,
    CupoExcedidoException,
    ValidacionException,
)


class PruebasControlEscolar(unittest.TestCase):
    """Pruebas unitarias que cubren casos normales, límites y errores."""

    def setUp(self):
        """Prepara un sistema limpio antes de cada prueba."""
        self.sistema = ControlEscolar()

    def test_alta_valida_y_propiedades_solo_lectura(self):
        """Acepta Alumno y Docente válidos, protege propiedades y usa super()."""
        alumno = Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad")
        docente = Docente("100000001", "Roberto Medina Ríos", "Ciencias Computacionales")
        self.sistema.registrar(alumno)
        self.sistema.registrar(docente)

        self.assertEqual(len(self.sistema.personas()), 2)
        self.assertIn("[219000001] Mariana Torres Vega", alumno.describir())
        self.assertIn("Carrera: Ciberseguridad", alumno.describir())
        self.assertIn("[100000001] Roberto Medina Ríos", docente.describir())
        self.assertIn("Departamento: Ciencias Computacionales", docente.describir())

        with self.assertRaises(AttributeError):
            alumno.codigo = "999999999"
        with self.assertRaises(AttributeError):
            docente.departamento = "Otro"

    def test_rechazo_codigo_formato_invalido(self):
        """Rechaza códigos que no tengan exactamente 9 dígitos numéricos."""
        for codigo_malo in ("12345678", "1234567890", "21900A001", "", "   ", None, True):
            with self.subTest(codigo=codigo_malo):
                with self.assertRaises(ValidacionException):
                    Alumno(codigo_malo, "Luis Ramírez Soto", "Ciberseguridad")

    def test_rechazo_campos_obligatorios_vacios(self):
        """Rechaza nombre, carrera, departamento, clave o nombre de materia vacíos."""
        with self.assertRaises(ValueError):
            Alumno("219000002", "   ", "Ciberseguridad")
        with self.assertRaises(ValueError):
            Alumno("219000002", "Luis Ramírez Soto", "")
        with self.assertRaises(ValueError):
            Docente("100000002", "Elena Morales Paz", None)
        with self.assertRaises(ValueError):
            Materia("   ", "Programación II", 10)
        with self.assertRaises(ValueError):
            Materia("IL352", "", 10)

    def test_rechazo_duplicados_y_tipo_invalido(self):
        """Rechaza códigos de persona repetidos, claves repetidas y objetos ajenos."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        with self.assertRaises(CodigoDuplicadoException):
            self.sistema.registrar(Docente("219000001", "Otro Nombre", "Matemáticas"))

        self.sistema.registrar(Materia("IL352", "Programación II", 10))
        with self.assertRaises(CodigoDuplicadoException):
            self.sistema.registrar(Materia("il352", "Programación Duplicada", 5))

        with self.assertRaises(ValidacionException):
            self.sistema.registrar("no es un objeto válido")

    def test_rechazo_cupo_invalido_en_materia(self):
        """Rechaza cupos menores o iguales a cero o de tipo no entero."""
        for cupo_malo in (0, -5, 2.5, "diez", True, None):
            with self.subTest(cupo=cupo_malo):
                with self.assertRaises(ValidacionException):
                    Materia("IL360", "Redes de Computadoras", cupo_malo)

    def test_inscripcion_normal_hasta_llenar_cupo_limite(self):
        """Permite inscribir hasta ocupar exactamente el último lugar disponible."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        self.sistema.registrar(Docente("100000001", "Roberto Medina Ríos", "Computación"))
        materia = Materia("IL352", "Programación II", 2)
        self.sistema.registrar(materia)

        self.sistema.asignar(219000001, "il352")
        self.sistema.asignar(" 100000001 ", "IL352")

        self.assertEqual(materia.inscritos, ("219000001", "100000001"))
        self.assertEqual(materia.lugares_disponibles, 0)

    def test_rechazo_cupo_excedido(self):
        """Lanza CupoExcedidoException cuando la materia ya alcanzó su cupo máximo."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        self.sistema.registrar(Alumno("219000002", "Luis Ramírez Soto", "Ciberseguridad"))
        self.sistema.registrar(Materia("IL352", "Programación II", 1))

        self.sistema.asignar("219000001", "IL352")
        with self.assertRaises(CupoExcedidoException):
            self.sistema.asignar("219000002", "IL352")

    def test_rechazo_doble_inscripcion_en_misma_materia(self):
        """Impide inscribir dos veces a la misma persona en la misma materia."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        self.sistema.registrar(Materia("IL352", "Programación II", 5))

        self.sistema.asignar("219000001", "IL352")
        with self.assertRaises(ValidacionException):
            self.sistema.asignar("219000001", "IL352")

    def test_rechazo_asignar_persona_o_materia_inexistentes(self):
        """Rechaza inscripciones si la persona o la materia no existen en el sistema."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        self.sistema.registrar(Materia("IL352", "Programación II", 5))

        with self.assertRaises(ValidacionException):
            self.sistema.asignar("299999999", "IL352")
        with self.assertRaises(ValidacionException):
            self.sistema.asignar("219000001", "XX999")

    def test_polimorfismo_listar_y_composicion_bitacora(self):
        """listar() muestra ambos tipos polimórficos y la bitácora anota los eventos."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        self.sistema.registrar(Docente("100000001", "Roberto Medina Ríos", "Computación"))
        self.sistema.registrar(Materia("IL352", "Programación II", 2))
        self.sistema.asignar("219000001", "IL352")

        with self.assertRaises(ValidacionException):
            self.sistema.asignar("219000001", "XX000")

        salida = io.StringIO()
        with redirect_stdout(salida):
            self.sistema.listar()
        texto = salida.getvalue()

        self.assertIn("Alumno   [219000001] Mariana Torres Vega | Carrera: Ciberseguridad", texto)
        self.assertIn("Docente  [100000001] Roberto Medina Ríos | Departamento: Computación", texto)
        self.assertIn("Materia  [IL352] Programación II", texto)
        self.assertTrue(any("Alta:" in e for e in self.sistema.bitacora.eventos))
        self.assertTrue(any("Inscripción rechazada:" in e for e in self.sistema.bitacora.eventos))

    def test_persistencia_guardar_y_cargar_completa(self):
        """Guarda todo el estado en JSON y lo reconstruye intacto en otro sistema."""
        self.sistema.registrar(Alumno("219000001", "Mariana Torres Vega", "Ciberseguridad"))
        self.sistema.registrar(Docente("100000001", "Roberto Medina Ríos", "Computación"))
        self.sistema.registrar(Materia("IL352", "Programación II", 3))
        self.sistema.asignar("219000001", "IL352")
        self.sistema.asignar("100000001", "IL352")

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "estado.json")
            guardar(self.sistema, ruta)

            nuevo = ControlEscolar()
            self.assertTrue(cargar(nuevo, ruta))
            self.assertEqual(len(nuevo.personas()), 2)
            self.assertIsInstance(nuevo.personas()[0], Alumno)
            self.assertIsInstance(nuevo.personas()[1], Docente)
            self.assertEqual(nuevo.materias()[0].inscritos, ("219000001", "100000001"))
            self.assertGreaterEqual(len(nuevo.bitacora.eventos), 5)

    def test_arranque_limpio_archivo_inexistente_o_danado(self):
        """Arranca vacío sin error si el archivo no existe o está corrupto."""
        with tempfile.TemporaryDirectory() as carpeta:
            inexistente = os.path.join(carpeta, "no_existe.json")
            self.assertFalse(cargar(self.sistema, inexistente))
            self.assertEqual(self.sistema.personas(), [])
            self.assertEqual(self.sistema.materias(), [])

            corrupto = os.path.join(carpeta, "danado.json")
            with open(corrupto, "w", encoding="utf-8") as archivo:
                archivo.write("{json roto")
            with redirect_stdout(io.StringIO()):
                self.assertFalse(ControlEscolar.cargar(self.sistema, corrupto))
            self.assertEqual(self.sistema.personas(), [])

            datos_alterados = {
                "personas": [{"tipo": "Alumno", "codigo": "abc", "nombre": "X", "carrera": "Y"}],
                "materias": [],
                "bitacora": [],
            }
            with open(corrupto, "w", encoding="utf-8") as archivo:
                json.dump(datos_alterados, archivo)
            with redirect_stdout(io.StringIO()):
                self.assertFalse(cargar(self.sistema, corrupto))
            self.assertEqual(self.sistema.personas(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

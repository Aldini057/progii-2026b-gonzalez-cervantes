"""Servidor web local para el Sistema de Control Escolar.

No requiere bibliotecas externas; utiliza el módulo http.server de la biblioteca
estándar de Python.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from almacen import cargar, guardar
from modelo import Alumno, Docente, Materia
from sistema import ControlEscolar
from validacion import ValidacionException

RUTA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_escolares.json")
PUERTO = 8000

# Instancia global del sistema
sistema = ControlEscolar()
cargar(sistema, RUTA_DATOS)


HTML_PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Control Escolar</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; }
  table { border-collapse: collapse; margin-bottom: 20px; }
  th, td { border: 1px solid #999; padding: 4px 8px; text-align: left; }
  th { background: #ddd; }
  fieldset { margin-bottom: 15px; width: 350px; }
  label { display: inline-block; width: 110px; }
  input, select { margin-bottom: 6px; }
  .contenedor { display: flex; gap: 30px; }
  .error { color: red; }
  .ok { color: green; }
  #bitacora { border: 1px solid #999; height: 200px; overflow-y: scroll; font-family: monospace; font-size: 12px; padding: 4px; }
</style>
</head>
<body>
<h1>Sistema de Control Escolar</h1>
<p>Programación II - CUGDL 2026B</p>
<button onclick="accionPersistencia('guardar')">Guardar</button>
<button onclick="accionPersistencia('cargar')">Cargar</button>
<hr>

<div class="contenedor">
<div>
  <fieldset>
    <legend>Registrar</legend>
    <label>Tipo:</label>
    <select id="reg-tipo" onchange="cambiarTipo()">
      <option>Alumno</option>
      <option>Docente</option>
      <option>Materia</option>
    </select><br>
    <div id="campo-persona">
      <label>Código:</label><input type="text" id="reg-codigo" maxlength="9"><br>
      <label>Nombre:</label><input type="text" id="reg-nombre"><br>
      <span id="grupo-carrera"><label>Carrera:</label><input type="text" id="reg-carrera"><br></span>
      <span id="grupo-depto" style="display:none"><label>Departamento:</label><input type="text" id="reg-depto"><br></span>
    </div>
    <div id="campo-materia" style="display:none">
      <label>Clave:</label><input type="text" id="reg-clave"><br>
      <label>Nombre:</label><input type="text" id="reg-nombre-materia"><br>
      <label>Cupo:</label><input type="number" id="reg-cupo" min="1"><br>
    </div>
    <button onclick="enviarRegistro()">Registrar</button>
    <p id="msg-registro"></p>
  </fieldset>

  <fieldset>
    <legend>Inscribir en materia</legend>
    <label>Código:</label><input type="text" id="asig-codigo"><br>
    <label>Clave materia:</label><input type="text" id="asig-clave"><br>
    <button onclick="enviarAsignar()">Inscribir</button>
    <p id="msg-asignar"></p>
  </fieldset>
</div>

<div>
  <h3>Personas</h3>
  <table>
    <thead><tr><th>Código</th><th>Tipo</th><th>Nombre</th><th>Carrera / Departamento</th></tr></thead>
    <tbody id="tabla-personas"></tbody>
  </table>

  <h3>Materias</h3>
  <table>
    <thead><tr><th>Clave</th><th>Nombre</th><th>Cupo</th><th>Inscritos</th></tr></thead>
    <tbody id="tabla-materias"></tbody>
  </table>
</div>
</div>

<h3>Bitácora</h3>
<div id="bitacora"></div>

<script>
function esc(texto) {
  const div = document.createElement('div');
  div.textContent = String(texto);
  return div.innerHTML;
}

function cambiarTipo() {
  const tipo = document.getElementById('reg-tipo').value;
  document.getElementById('campo-persona').style.display = tipo === 'Materia' ? 'none' : 'block';
  document.getElementById('campo-materia').style.display = tipo === 'Materia' ? 'block' : 'none';
  document.getElementById('grupo-carrera').style.display = tipo === 'Alumno' ? 'inline' : 'none';
  document.getElementById('grupo-depto').style.display = tipo === 'Docente' ? 'inline' : 'none';
}

function mostrarMensaje(id, texto, ok) {
  const p = document.getElementById(id);
  p.className = ok ? 'ok' : 'error';
  p.textContent = texto;
}

async function cargarEstado() {
  const res = await fetch('/api/estado');
  const data = await res.json();

  const personas = document.getElementById('tabla-personas');
  personas.innerHTML = data.personas.map(p =>
    `<tr><td>${esc(p.codigo)}</td><td>${esc(p.tipo)}</td><td>${esc(p.nombre)}</td><td>${esc(p.detalle)}</td></tr>`
  ).join('') || '<tr><td colspan="4">Sin registros</td></tr>';

  const materias = document.getElementById('tabla-materias');
  materias.innerHTML = data.materias.map(m =>
    `<tr><td>${esc(m.clave)}</td><td>${esc(m.nombre)}</td><td>${m.inscritos.length}/${m.cupo_maximo}</td><td>${esc(m.inscritos.join(', ') || '-')}</td></tr>`
  ).join('') || '<tr><td colspan="4">Sin registros</td></tr>';

  const bitacora = document.getElementById('bitacora');
  bitacora.innerHTML = data.bitacora.map(e => `<div>${esc(e)}</div>`).join('');
  bitacora.scrollTop = bitacora.scrollHeight;
}

async function enviar(url, datos, idMensaje) {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });
    const result = await res.json();
    mostrarMensaje(idMensaje, res.ok ? result.mensaje : result.error, res.ok);
    cargarEstado();
    return res.ok;
  } catch (e) {
    mostrarMensaje(idMensaje, 'Error de conexión', false);
    return false;
  }
}

async function enviarRegistro() {
  const tipo = document.getElementById('reg-tipo').value;
  const datos = { tipo };
  if (tipo === 'Materia') {
    datos.clave = document.getElementById('reg-clave').value;
    datos.nombre = document.getElementById('reg-nombre-materia').value;
    datos.cupo = document.getElementById('reg-cupo').value;
  } else {
    datos.codigo = document.getElementById('reg-codigo').value;
    datos.nombre = document.getElementById('reg-nombre').value;
    datos.carrera = document.getElementById('reg-carrera').value;
    datos.departamento = document.getElementById('reg-depto').value;
  }
  if (await enviar('/api/registrar', datos, 'msg-registro')) {
    document.querySelectorAll('fieldset input').forEach(i => i.value = '');
  }
}

async function enviarAsignar() {
  const codigo = document.getElementById('asig-codigo').value;
  const clave = document.getElementById('asig-clave').value;
  await enviar('/api/asignar', { codigo, clave }, 'msg-asignar');
}

async function accionPersistencia(tipo) {
  const res = await fetch('/api/' + tipo, { method: 'POST' });
  const result = await res.json();
  alert(result.mensaje || result.error);
  cargarEstado();
}

cargarEstado();
</script>
</body>
</html>
"""


class ManejadorControlEscolar(BaseHTTPRequestHandler):
    """Manejador HTTP para la interfaz web y la API REST."""

    def log_message(self, format, *args):
        """Silencia los logs normales por consola para una salida más limpia."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def _responder_json(self, codigo, datos):
        """Serializa datos como JSON y envía la respuesta HTTP."""
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        """Sirve la página principal o devuelve el estado actual en JSON."""
        url = urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            cuerpo = HTML_PAGINA.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
            return

        if url.path == "/api/estado":
            personas = []
            for p in sistema.personas():
                datos_p = p.a_dict()
                detalle = datos_p.get("carrera") or datos_p.get("departamento", "")
                personas.append({
                    "codigo": p.codigo,
                    "nombre": p.nombre,
                    "tipo": p.tipo,
                    "detalle": detalle
                })

            materias = []
            for m in sistema.materias():
                materias.append({
                    "clave": m.clave,
                    "nombre": m.nombre,
                    "cupo_maximo": m.cupo_maximo,
                    "lugares": m.lugares_disponibles,
                    "inscritos": list(m.inscritos)
                })

            self._responder_json(200, {
                "personas": personas,
                "materias": materias,
                "bitacora": list(sistema.bitacora.eventos)
            })
            return

        self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        """Procesa altas, inscripciones y operaciones de persistencia vía POST."""
        url = urlparse(self.path)
        longitud = int(self.headers.get("Content-Length", 0))
        cuerpo = self.rfile.read(longitud).decode("utf-8") if longitud > 0 else "{}"
        try:
            datos = json.loads(cuerpo) if cuerpo else {}
        except Exception:
            self._responder_json(400, {"ok": False, "error": "JSON malformado"})
            return

        if url.path == "/api/registrar":
            tipo = datos.get("tipo")
            try:
                if tipo == "Alumno":
                    obj = Alumno(datos.get("codigo"), datos.get("nombre"), datos.get("carrera"))
                elif tipo == "Docente":
                    obj = Docente(datos.get("codigo"), datos.get("nombre"), datos.get("departamento"))
                elif tipo == "Materia":
                    cupo = int(datos.get("cupo", 0)) if str(datos.get("cupo", "")).isdigit() else datos.get("cupo")
                    obj = Materia(datos.get("clave"), datos.get("nombre"), cupo)
                else:
                    raise ValidacionException(f"Tipo no soportado: {tipo}")

                sistema.registrar(obj)
                guardar(sistema, RUTA_DATOS)
                self._responder_json(200, {"ok": True, "mensaje": f"{tipo} registrado exitosamente."})
            except Exception as e:
                self._responder_json(400, {"ok": False, "error": str(e)})
            return

        if url.path == "/api/asignar":
            codigo = datos.get("codigo")
            clave = datos.get("clave")
            try:
                sistema.asignar(codigo, clave)
                guardar(sistema, RUTA_DATOS)
                self._responder_json(200, {"ok": True, "mensaje": f"Persona {codigo} inscrita en {clave}."})
            except Exception as e:
                self._responder_json(400, {"ok": False, "error": str(e)})
            return

        if url.path == "/api/guardar":
            try:
                guardar(sistema, RUTA_DATOS)
                self._responder_json(200, {"ok": True, "mensaje": f"Guardado en {os.path.basename(RUTA_DATOS)}."})
            except Exception as e:
                self._responder_json(500, {"ok": False, "error": str(e)})
            return

        if url.path == "/api/cargar":
            try:
                cargar(sistema, RUTA_DATOS)
                self._responder_json(200, {"ok": True, "mensaje": f"Recargado desde {os.path.basename(RUTA_DATOS)}."})
            except Exception as e:
                self._responder_json(500, {"ok": False, "error": str(e)})
            return

        self.send_error(404, "Endpoint no encontrado")


def iniciar_servidor(puerto=PUERTO):
    """Inicia el servidor HTTP local en el puerto indicado."""
    servidor = HTTPServer(("0.0.0.0", puerto), ManejadorControlEscolar)
    print(f"Servidor iniciado en http://localhost:{puerto}")
    print("Presiona Ctrl+C para detenerlo.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PUERTO
    iniciar_servidor(puerto)

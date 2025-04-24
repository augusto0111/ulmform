# app.py
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_bcrypt import Bcrypt
import os
import subprocess
import re
import sqlite3
import math
from datetime import datetime
from database import init_db
from flask import send_from_directory
import mercadopago

sdk = mercadopago.SDK("TEST-1642651305176873-042019-c2d34e50d2285e0d38aa9e1451727e7d-352748090")  # reemplaza con tu token real



app = Flask(__name__)
app.secret_key = "clave-secreta"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
bcrypt = Bcrypt(app)

init_db()
DB = "pedidos.db"

@app.route('/')
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT nombre FROM materiales")
    materiales = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template('index.html', materiales=materiales)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios (username, email, password) VALUES (?, ?, ?)",
                          (username, email, hashed))
                conn.commit()
                return redirect('/login')
            except sqlite3.IntegrityError:
                return "❌ El usuario o email ya existe"
    return render_template("registro.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT password FROM usuarios WHERE username = ?", (username,))
        usuario = c.fetchone()
        conn.close()
        if usuario and bcrypt.check_password_hash(usuario[0], password):
            session['usuario'] = username
            return redirect('/')
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT password FROM admin WHERE nombre = ?", (nombre,))
        admin = c.fetchone()
        conn.close()
        if admin and bcrypt.check_password_hash(admin[0], password):
            session['admin'] = nombre
            return redirect('/admin/precios')
        else:
            return render_template("login_admin.html", error="Credenciales incorrectas")
    return render_template("login_admin.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/subir', methods=['POST'])
def subir_archivo():
    archivo = request.files.get('archivo')
    #print("📦 Archivo recibido:", archivo.filename if archivo else "Nada")

    try:
        tecnologia = request.form.get("tecnologia", "FDM")
        material = request.form.get("material")
        infill = int(request.form.get("infill", 20))
        cantidad = int(request.form.get("cantidad", 1))
        print(f"📄 Parámetros: tecnologia={tecnologia}, material={material}, infill={infill}, cantidad={cantidad}")

        if not archivo or not archivo.filename.endswith('.stl'):
            return jsonify({"error": "Archivo inválido o no se envió correctamente"}), 400

        filename = archivo.filename.replace(" ", "_")
        ruta_stl = os.path.join(UPLOAD_FOLDER, filename)
        archivo.save(ruta_stl)

        output_gcode = os.path.join(UPLOAD_FOLDER, filename.replace(".stl", ".gcode"))

        comando = [
            "C:\\Slic3r\\Slic3r-1.3.0.64bit\\slic3r-console.exe",
            ruta_stl,
            "--fill-density", f"{infill}%",
            "--support-material",
            "--perimeters", "3",
            "--filament-diameter", "1.75",
            "--nozzle-diameter", "0.4",
            "--layer-height", "0.2",
            "--output", output_gcode
        ]

        salida = subprocess.check_output(comando, stderr=subprocess.STDOUT, text=True)
        print("✅ Slicer ejecutado correctamente:")
        print(salida)

        filamento_mm = analizar_filamento(output_gcode)
        print("📏 Filamento usado (mm):", filamento_mm)

        precio, gramos = calcular_precio(filamento_mm, material)
        total = round(precio * cantidad, 2)

        cotizacion = {
            "archivo": filename,
            "tecnologia": tecnologia,
            "material": material,
            "infill": infill,
            "cantidad": cantidad,
            "gramos": gramos,
            "minutos": 0,
            "precio_unitario": precio,
            "total": float (total)
        }

        print("✅ Cotización generada:", cotizacion)
        session["ultima_cotizacion"] = cotizacion
        return jsonify(cotizacion)

    except subprocess.CalledProcessError as e:
        print("❌ Error en slicing:", e.output)
        return jsonify({"error": "Error al hacer slicing", "detalles": e.output}), 500
    except Exception as ex:
        print("❌ Error inesperado en /subir:")
        print(ex)
        return jsonify({"error": "Error inesperado en el servidor"}), 500



@app.route('/admin/precios', methods=["GET", "POST"])
def admin_precios():
    if 'admin' not in session:
        return redirect('/login_admin')

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == "POST":
        for nombre in request.form:
            nuevo_precio = request.form[nombre]
            if nuevo_precio:
                c.execute("UPDATE materiales SET precio_por_kg = ? WHERE nombre = ?", (float(nuevo_precio), nombre))
        conn.commit()

    c.execute("SELECT nombre, precio_por_kg FROM materiales")
    materiales = {nombre: precio for nombre, precio in c.fetchall()}
    conn.close()
    return render_template("admin_precios.html", precios=materiales)

@app.route("/admin/revisar_pedidos")
def admin_revisar_pedidos():
    if "admin" not in session:
        return redirect("/login_admin")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Mostrar solo pedidos que están en revisión y tienen estado 'pendiente'
    c.execute("""
        SELECT p.id, p.usuario, p.archivo, p.tecnologia, p.material, p.infill, p.cantidad,
               p.gramos, p.precio_unitario, p.total, p.fecha
        FROM pedidos p
        INNER JOIN revisiones_admin r ON p.id = r.pedido_id
        WHERE r.estado = 'pendiente'
        ORDER BY p.fecha DESC
    """)
    pendientes = c.fetchall()
    conn.close()

    return render_template("admin_revisar_pedidos.html", pedidos=pendientes)



@app.route("/admin/revision/<int:pedido_id>")
def revisar_pedido(pedido_id):
    if "admin" not in session:
        return redirect("/login_admin")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = c.fetchone()
    conn.close()

    if not pedido:
        return "Pedido no encontrado", 404

    return render_template("admin_revision.html", pedido=pedido)


@app.route("/admin/revision/<int:id>", methods=["POST"])
def procesar_revision(id):
    if "admin" not in session:
        return redirect("/login_admin")

    accion = request.form.get("accion")
    motivo = request.form.get("motivo", "").strip()

    print(f"📋 Procesando revisión del pedido {id} con acción: {accion}")

    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        if accion == "aprobar":
            c.execute("""
                UPDATE pedidos
                SET estado = 'aprobado',
                    notificacion = 'Tu pedido ha sido aprobado y está listo para pagar.'
                WHERE id = ?
            """, (id,))
            c.execute("DELETE FROM revisiones_admin WHERE pedido_id = ?", (id,))
            print(f"✅ Pedido {id} aprobado y revisión eliminada.")

        elif accion == "rechazar":
            texto_motivo = motivo if motivo else "El administrador rechazó el pedido por razones no especificadas."
            c.execute("""
                UPDATE pedidos
                SET estado = 'rechazado',
                    notificacion = ?
                WHERE id = ?
            """, (texto_motivo, id))
            c.execute("DELETE FROM revisiones_admin WHERE pedido_id = ?", (id,))
            print(f"❌ Pedido {id} rechazado y revisión eliminada.")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"❌ Error al procesar revisión del pedido {id}: {e}")

    return redirect("/admin/revisar_pedidos")






@app.route("/pagar/<int:id>", methods=["POST"])
def pagar_pedido(id):
    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE pedidos SET estado = 'pagado', notificacion = 'Pago recibido. ¡Gracias!' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/historial")


@app.route("/admin/agregar_material", methods=["POST"])
def agregar_material():
    if 'admin' not in session:
        return redirect('/login_admin')

    nombre = request.form["nuevo_material"].strip()
    precio = request.form["nuevo_precio"]

    if not nombre or not precio:
        return redirect("/admin/precios")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO materiales (nombre, precio_por_kg) VALUES (?, ?)", (nombre, float(precio)))
    conn.commit()
    conn.close()

    return redirect("/admin/precios")


def analizar_filamento(gcode_path):
    filamento_mm = 0.0
    with open(gcode_path, "r", encoding="utf-8", errors="ignore") as archivo:
        for linea in archivo:
            if "filament used =" in linea.lower():
                match = re.search(r"([\d.]+)\s*mm", linea)
                if match:
                    filamento_mm = float(match.group(1))
                    break
    return filamento_mm




def calcular_precio(filamento_mm, material):
    # Parámetros estándar para PLA, ABS, PETG
    DENSIDAD_MATERIAL = {
        "PLA": 1.24,
        "ABS": 1.04,
        "PETG": 1.27
    }

    diametro = 1.75  # mm
    radio = diametro / 2
    volumen_mm3 = math.pi * (radio ** 2) * filamento_mm
    volumen_cm3 = volumen_mm3 * 0.001  # mm³ → cm³

    # Densidad por defecto si el material no está en el diccionario
    densidad = DENSIDAD_MATERIAL.get(material.upper(), 1.24)

    gramos = volumen_cm3 * densidad
    gramos = round(gramos, 2)

    # Obtener precio por kg desde base de datos
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT precio_por_kg FROM materiales WHERE nombre = ?", (material,))
    resultado = c.fetchone()
    conn.close()

    if not resultado:
        return 0.0, gramos

    precio_por_gramo = resultado[0] / 1000
    precio = round(gramos * precio_por_gramo, 2)

    return precio, gramos



# ========================
# VER CARRITO
# ========================
@app.route('/carrito')
def ver_carrito():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("carrito.html", carrito=session.get("carrito", []))

# ========================
# CONFIRMAR TODO EL CARRITO
# ========================
@app.route('/confirmar', methods=['POST'])
def confirmar_pedido():
    if 'usuario' not in session:
        return jsonify({"error": "Debés iniciar sesión para confirmar el pedido"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No hay datos para confirmar"}), 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Insertar el pedido en la tabla pedidos
    c.execute("""
        INSERT INTO pedidos (usuario, archivo, tecnologia, material, infill, cantidad, gramos, minutos, precio_unitario, total, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session['usuario'],
        data['archivo'],
        data['tecnologia'],
        data['material'],
        data['infill'],
        data['cantidad'],
        data['gramos'],
        data['minutos'],
        data['precio_unitario'],
        data['total'],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    # 🔥 Insertar en revisiones_admin
    pedido_id = c.lastrowid
    c.execute("INSERT INTO revisiones_admin (pedido_id) VALUES (?)", (pedido_id,))

    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Pedido confirmado."})


@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if "usuario" not in session:
        return jsonify({"error": "Debés iniciar sesión para usar el carrito."}), 401

    try:
        data = request.get_json()
        print("📥 Datos recibidos para agregar al carrito:", data)

        if not data:
            return jsonify({"error": "No hay cotización activa para agregar."}), 400

        # ✅ Convertimos datos clave a float para evitar errores en la sesión
        data["total"] = float(data.get("total", 0))
        data["precio_unitario"] = float(data.get("precio_unitario", 0))
        data["gramos"] = float(data.get("gramos", 0))

        import json
        print("🧪 JSON serializable:", json.dumps(data))  # Ayuda a detectar errores ocultos

        session.setdefault("carrito", []).append(data)
        session.modified = True
        return jsonify({"mensaje": "🛒 Producto agregado al carrito."})

    except Exception as e:
        print("❌ Error en /agregar_carrito:", e)
        return jsonify({"error": "Error interno en el servidor"}), 500




@app.route('/confirmar_carrito', methods=['POST'])
def confirmar_carrito():
    if "usuario" not in session:
        return jsonify({"error": "Debés iniciar sesión para confirmar el carrito"}), 401

    carrito = session.get("carrito", [])
    if not carrito:
        return jsonify({"error": "El carrito está vacío"}), 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    for item in carrito:
        c.execute("""
            INSERT INTO pedidos (usuario, archivo, tecnologia, material, infill, cantidad, gramos, minutos, precio_unitario, total, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["usuario"],
            item.get("archivo", "sin_nombre"),
            item.get("tecnologia", "FDM"),
            item.get("material"),
            item.get("infill", 20),
            item.get("cantidad"),
            item.get("gramos", 0),
            item.get("minutos", 0),
            item.get("precio_unitario"),
            item.get("total"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        # 🔥 Insertar en revisiones_admin
        pedido_id = c.lastrowid
        c.execute("INSERT INTO revisiones_admin (pedido_id) VALUES (?)", (pedido_id,))

    conn.commit()
    conn.close()
    session["carrito"] = []
    return jsonify({"mensaje": "✅ Carrito confirmado y pedidos guardados con éxito."})



# ========================
# HISTORIAL DE PEDIDOS
# ========================
@app.route("/historial")
def historial():
    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM pedidos WHERE usuario = ? ORDER BY fecha DESC", (session["usuario"],))
    pedidos = c.fetchall()
    conn.close()

    return render_template("historial.html", pedidos=pedidos)


@app.route('/eliminar_carrito', methods=['POST'])
def eliminar_carrito():
    if "usuario" not in session:
        return jsonify({"error": "No has iniciado sesión"}), 401

    indice = request.get_json().get("indice")
    if indice is not None and "carrito" in session and 0 <= indice < len(session["carrito"]):
        session["carrito"].pop(indice)
        session.modified = True
        return jsonify({"mensaje": "🗑️ Producto eliminado del carrito"})
    return jsonify({"error": "Índice inválido"}), 400

@app.route('/uploads/<path:filename>')
def archivos_subidos(filename):
    return send_from_directory("uploads", filename)

from flask import request  # asegurate de tenerlo importado arriba

from flask import request  # Asegurate de tener esto importado arriba

@app.route("/crear_pago/<int:pedido_id>", methods=["POST"])
def crear_pago(pedido_id):
    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT archivo, material, total FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = c.fetchone()
    conn.close()

    if not pedido:
        return "Pedido no encontrado", 404

    archivo, material, total = pedido

    if not total or float(total) <= 0:
        return "Error: Total inválido", 400

    preference_data = {
        "items": [{
            "title": f"Impresión 3D - {archivo}",
            "description": f"Material: {material}",
            "quantity": 1,
            "currency_id": "ARS",
            "unit_price": float(total)
        }],
        "back_urls": {
            "success": request.host_url + f"pago_exitoso/{pedido_id}",
            "failure": request.host_url + "pago_fallido",
            "pending": request.host_url + "pago_pendiente"
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)
    print("🧾 Respuesta de MercadoPago:", preference_response)

    try:
        return redirect(preference_response["response"]["init_point"])
    except KeyError:
        return f"❌ Error al generar preferencia: {preference_response}", 500




@app.route("/pago_exitoso/<int:pedido_id>")
def pago_exitoso(pedido_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE pedidos SET estado = 'pagado', notificacion = '✅ ¡Pago confirmado!' WHERE id = ?", (pedido_id,))
    conn.commit()
    conn.close()
    return redirect("/historial")

@app.route("/pago_fallido")
def pago_fallido():
    return "<h2>❌ Hubo un problema con el pago.</h2><a href='/historial'>Volver al historial</a>"

@app.route("/pago_pendiente")
def pago_pendiente():
    return "<h2>🕐 Tu pago está pendiente de confirmación.</h2><a href='/historial'>Volver al historial</a>"


@app.route("/produccion")
def vista_produccion():
    if "admin" not in session:
        return redirect("/login_admin")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT id, fecha, usuario, archivo, material, infill, cantidad, gramos, estado
        FROM pedidos
        WHERE estado = 'pagado'
        ORDER BY fecha ASC
    """)
    pedidos = c.fetchall()
    conn.close()

    return render_template("produccion.html", pedidos=pedidos)


@app.route("/marcar_entregado/<int:pedido_id>", methods=["POST"])
def marcar_entregado(pedido_id):
    if "admin" not in session:
        return redirect("/login_admin")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        UPDATE pedidos
        SET estado = 'entregado',
            notificacion = '🟢 Tu pedido fue entregado.'
        WHERE id = ?
    """, (pedido_id,))
    conn.commit()
    conn.close()

    return redirect("/produccion")



if __name__ == "__main__":
    app.run(debug=True)

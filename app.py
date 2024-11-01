from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configuración de Pusher
pusher_client = pusher.Pusher(
    app_id="1714541",
    key="2df86616075904231311",
    secret="2f91d936fd43d8e85a1a",
    cluster="us2",
    ssl=True
)

# Función para obtener una nueva conexión a la base de datos
def get_db_connection():
    try:
        con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
        )
        return con
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Ruta principal
@app.route("/")
def index():
    return render_template("app.html")

# Ruta para alumnos
@app.route("/alumnos")
def alumnos():
    return render_template("alumnos.html")

# Ruta para guardar alumnos
@app.route("/alumnos/guardar", methods=["POST"])
def alumnos_guardar():
    matricula = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]
    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

# Función para notificar actualización de contacto
def notificar_actualizacion_contacto(mensaje):
    pusher_client.trigger("canalRegistrosContacto", "registroContacto", {"mensaje": mensaje})

# Ruta para buscar contactos
@app.route("/buscar")
def buscar():
    con = get_db_connection()
    if not con:
        return make_response(jsonify({"error": "Error al conectar a la base de datos"}), 500)

    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute("""
        SELECT Id_Contacto, Correo_Electronico, Nombre, Asunto 
        FROM tst0_contacto
        ORDER BY Id_Contacto DESC
        LIMIT 10 OFFSET 0
        """)
        registros = cursor.fetchall()
        return make_response(jsonify(registros))
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return make_response(jsonify({"error": "Error al obtener los datos"}), 500)
    finally:
        cursor.close()
        con.close()

# Ruta para guardar contactos
@app.route("/guardar", methods=["POST"])
def guardar():
    con = get_db_connection()
    if not con:
        return make_response(jsonify({"error": "Error al conectar a la base de datos"}), 500)

    try:
        id = request.form["id"]
        correo_electronico = request.form["correo_electronico"]
        nombre = request.form["nombre"]
        asunto = request.form["asunto"]

        cursor = con.cursor()

        if id:
            sql = """
            UPDATE tst0_contacto SET
            Correo_Electronico = %s,
            Nombre = %s,
            Asunto = %s
            WHERE Id_Contacto = %s
            """
            val = (correo_electronico, nombre, asunto, id)
        else:
            sql = """
            INSERT INTO tst0_contacto (Correo_Electronico, Nombre, Asunto)
                            VALUES (%s, %s, %s)
            """
            val = (correo_electronico, nombre, asunto)

        cursor.execute(sql, val)
        con.commit()

        # Notificar la actualización
        notificar_actualizacion_contacto("Contacto actualizado")

        return make_response(jsonify({}))
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return make_response(jsonify({"error": "Error al guardar el contacto"}), 500)
    finally:
        cursor.close()
        con.close()

# Ruta para editar contactos
@app.route("/editar", methods=["GET"])
def editar():
    con = get_db_connection()
    if not con:
        return make_response(jsonify({"error": "Error al conectar a la base de datos"}), 500)

    try:
        id = request.args["id"]

        cursor = con.cursor(dictionary=True)
        sql = """
        SELECT Id_Contacto, Correo_Electronico, Nombre, Asunto 
        FROM tst0_contacto
        WHERE Id_Contacto = %s
        """
        val = (id,)
        cursor.execute(sql, val)
        registros = cursor.fetchall()
        return make_response(jsonify(registros))
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return make_response(jsonify({"error": "Error al obtener el contacto"}), 500)
    finally:
        cursor.close()
        con.close()

# Ruta para eliminar contactos
@app.route("/eliminar", methods=["POST"])
def eliminar():
    con = get_db_connection()
    if not con:
        return make_response(jsonify({"error": "Error al conectar a la base de datos"}), 500)

    try:
        id = request.form["id"]

        cursor = con.cursor()
        sql = """
        DELETE FROM tst0_contacto
        WHERE Id_Contacto = %s
        """
        val = (id,)
        cursor.execute(sql, val)
        con.commit()

        # Notificar la eliminación
        notificar_actualizacion_contacto("Contacto eliminado")

        return make_response(jsonify({}))
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return make_response(jsonify({"error": "Error al eliminar el contacto"}), 500)
    finally:
        cursor.close()
        con.close()

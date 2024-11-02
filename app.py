from flask import Flask, render_template, request, jsonify, make_response
import mysql.connector
import pusher
import logging

# Configura el logger de Flask
logging.basicConfig(level=logging.INFO)

# Conexión a la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

# Página principal que carga el CRUD de usuarios
@app.route("/")
def index():
    logging.info("Cargando página principal")
    con.close()
    return render_template("app.html")

# Crear o actualizar un usuario
@app.route("/usuarios/guardar", methods=["POST"])
def usuariosGuardar():
    if not con.is_connected():
        con.reconnect()

    id_usuario = request.form.get("id_usuario")
    nombre_usuario = request.form["nombre_usuario"]
    contrasena = request.form["contrasena"]

    cursor = con.cursor()
    if id_usuario:  # Actualizar
        sql = """
        UPDATE tst0_usuarios SET Nombre_Usuario = %s, Contrasena = %s WHERE Id_Usuario = %s
        """
        val = (nombre_usuario, contrasena, id_usuario)
        logging.info(f"Actualizando usuario con ID: {id_usuario}")
    else:  # Crear nuevo usuario
        sql = """
        INSERT INTO tst0_usuarios (Nombre_Usuario, Contrasena) VALUES (%s, %s)
        """
        val = (nombre_usuario, contrasena)
        logging.info(f"Creando nuevo usuario: {nombre_usuario}")

    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    con.close()

    notificar_actualizacion_usuarios()

    return make_response(jsonify({"message": "Usuario guardado exitosamente"}))

# Obtener todos los usuarios
@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tst0_usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    con.close()

    logging.info("Obteniendo lista de usuarios")
    return make_response(jsonify(usuarios))

# Obtener un usuario por su ID sin usar query string
@app.route("/usuarios/editar/<int:id_usuario>", methods=["GET"])
def editar_usuario(id_usuario):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql = "SELECT * FROM tst0_usuarios WHERE Id_Usuario = %s"
    val = (id_usuario,)
    cursor.execute(sql, val)
    usuario = cursor.fetchone()
    cursor.close()
    con.close()

    logging.info(f"Obteniendo datos del usuario con ID: {id_usuario}")
    return make_response(jsonify(usuario))

# Eliminar un usuario usando el ID en la URL
@app.route("/usuarios/eliminar/<int:id_usuario>", methods=["POST"])
def eliminar_usuario(id_usuario):
    logging.info(f"Intentando eliminar el usuario con ID: {id_usuario}")
   
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    sql = "DELETE FROM tst0_usuarios WHERE Id_Usuario = %s"
    val = (id_usuario,)
    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    con.close()

    notificar_actualizacion_usuarios()

    logging.info(f"Usuario con ID {id_usuario} eliminado exitosamente.")
    return make_response(jsonify({"message": "Usuario eliminado exitosamente"}))

# Notificar a través de Pusher sobre actualizaciones en la tabla de usuarios
def notificar_actualizacion_usuarios():
    import pusher
    pusher_client = pusher.Pusher(
        app_id="1889712",
        key="3a925c9457e124cf2fbb",
        secret="d5e38d90ae87e6b3f09a",
        cluster="us2",
        ssl=True
    )
    pusher_client.trigger("canalUsuarios", "actualizacion", {})
    logging.info("Notificación enviada a través de Pusher")

if __name__ == "__main__":
    app.run(debug=True)

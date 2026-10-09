
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import bcrypt
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)


# Conexion a la base de datos
def conectar(host, user, vpass, vdb):
    conn = pymysql.connect(
        host=host,
        user=user,
        password=vpass,
        database=vdb,
        charset="utf8mb4"
    )
    return conn


# Consultar todos los registros
@app.route("/", methods=["GET"])
def consulta_general():
    try:
        conn = conectar("localhost", "root", "admin", "gestor_contrasena")
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall()

        data = []
        for row in datos:
            data.append({
                "id_baul": row[0],
                "Plataforma": row[1],
                "usuario": row[2],
                "clave": row[3]
            })

        cur.close()
        conn.close()

        return jsonify({
            "baul": data,
            "mensaje": "Baul de contrasenas"
        }), 200

    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error"}), 500


# Consultar un registro por su ID
@app.route("/consulta_individual/<int:codigo>", methods=["GET"])
def consulta_individual(codigo):
    try:
        conn = conectar("localhost", "root", "admin", "gestor_contrasena")
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM baul WHERE id_baul = %s",
            (codigo,)
        )
        dato = cur.fetchone()

        cur.close()
        conn.close()

        if dato:
            data = {
                "id_baul": dato[0],
                "Plataforma": dato[1],
                "usuario": dato[2],
                "clave": dato[3]
            }
            return jsonify({
                "baul": data,
                "mensaje": "Registro encontrado"
            }), 200

        return jsonify({"mensaje": "Registro no encontrado"}), 404

    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error"}), 500


# Registrar una nueva contrasena
@app.route("/registro/", methods=["POST"])
def registro():
    try:
        data = request.get_json()

        if not data or not all(
            campo in data for campo in ("plataforma", "usuario", "clave")
        ):
            return jsonify({"mensaje": "Faltan datos"}), 400

        plataforma = data["plataforma"]
        usuario = data["usuario"]
        clave = data["clave"]

        clave_hash = bcrypt.hashpw(
            clave.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn = conectar("localhost", "root", "admin", "gestor_contrasena")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO baul (Plataforma, usuario, clave) "
            "VALUES (%s, %s, %s)",
            (plataforma, usuario, clave_hash)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensaje": "Registro agregado"}), 201

    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error"}), 500


# Eliminar un registro por ID
@app.route("/eliminar/<int:codigo>", methods=["DELETE"])
def eliminar(codigo):
    try:
        conn = conectar("localhost", "root", "admin", "gestor_contrasena")
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM baul WHERE id_baul = %s",
            (codigo,)
        )
        conn.commit()
        eliminado = cur.rowcount

        cur.close()
        conn.close()

        if eliminado:
            return jsonify({"mensaje": "Eliminado"}), 200

        return jsonify({"mensaje": "Registro no encontrado"}), 404

    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error"}), 500


# Actualizar un registro por ID
@app.route("/actualizar/<int:codigo>", methods=["PUT"])
def actualizar(codigo):
    try:
        data = request.get_json()

        if not data or not all(
            campo in data for campo in ("plataforma", "usuario", "clave")
        ):
            return jsonify({"mensaje": "Faltan datos"}), 400

        plataforma = data["plataforma"]
        usuario = data["usuario"]
        clave = data["clave"]

        clave_hash = bcrypt.hashpw(
            clave.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn = conectar("localhost", "root", "admin", "gestor_contrasena")
        cur = conn.cursor()

        cur.execute(
            "UPDATE baul SET Plataforma = %s, usuario = %s, clave = %s "
            "WHERE id_baul = %s",
            (plataforma, usuario, clave_hash, codigo)
        )

        conn.commit()
        actualizado = cur.rowcount

        cur.close()
        conn.close()

        if actualizado:
            return jsonify({"mensaje": "Registro actualizado"}), 200

        return jsonify(
            {"mensaje": "Registro no encontrado o sin cambios"}
        ), 404

    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error"}), 500


if __name__ == "__main__":
    app.run(debug=True)

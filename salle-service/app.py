import psycopg2
from flask import Flask, jsonify, request, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'salle-secret'  # pour les sessions

def get_db_connection():
    return psycopg2.connect(
        host="salle-db",
        database="salles",
        user="postgres",
        password="postgres"
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS salles (
            id SERIAL PRIMARY KEY,
            nom TEXT NOT NULL,
            capacite INTEGER NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def require_role(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            if session['user'].get('role') != role:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

@app.route('/')
def home():
    return jsonify({"message": "Salle service is running 🏢"})

@app.route('/salles', methods=['GET'])
def get_salles():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM salles;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{"id": r[0], "nom": r[1], "capacite": r[2]} for r in rows])

@app.route('/salles/<int:id>', methods=['GET'])
def get_salle(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM salles WHERE id = %s;", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify({"id": row[0], "nom": row[1], "capacite": row[2]})
    return jsonify({"error": "Salle not found"}), 404

@app.route('/salles', methods=['POST'])
@require_role("Admin")
def create_salle():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO salles (nom, capacite)
        VALUES (%s, %s)
        RETURNING id;
    """, (data['nom'], data['capacite']))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id}), 201

@app.route('/salles/<int:id>', methods=['PUT'])
@require_role("Admin")
def update_salle(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE salles
        SET nom = %s, capacite = %s
        WHERE id = %s;
    """, (data['nom'], data['capacite'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Salle updated"})

@app.route('/salles/<int:id>', methods=['DELETE'])
@require_role("Admin")
def delete_salle(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM salles WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Salle deleted"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5002)




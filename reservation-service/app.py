import psycopg2
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
from flask import Flask, jsonify, request, session
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ---------------------------- RBAC ----------------------------
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

# ------------------------ Kafka Setup ------------------------
def create_kafka_producer():
    for i in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Kafka Producer connecté")
            return producer
        except NoBrokersAvailable:
            print(f"⏳ Kafka pas prêt, tentative {i+1}/10...")
            time.sleep(5)
    raise Exception("❌ Échec de connexion à Kafka")

producer = create_kafka_producer()

# ------------------------- PostgreSQL -------------------------
def get_db_connection():
    return psycopg2.connect(
        host="reservation-db",
        database="reservations",
        user="postgres",
        password="postgres"
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            titre TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            salle_id INTEGER NOT NULL,
            date DATE NOT NULL,
            heure TIME NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# -------------------------- ROUTES ---------------------------
@app.route('/')
def home():
    return jsonify({"message": "Reservation service is running 📅"})

@app.route('/reservations', methods=['GET'])
@require_role("Admin")
def get_all():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reservations;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = [
        {
            "id": row[0],
            "titre": row[1],
            "user_id": row[2],
            "salle_id": row[3],
            "date": row[4].isoformat(),
            "heure": row[5].strftime("%H:%M")
        } for row in rows
    ]
    return jsonify(results)

@app.route('/reservations/<int:id>', methods=['GET'])
@require_role("Admin")
def get_one(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reservations WHERE id = %s;", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return jsonify({
            "id": row[0],
            "titre": row[1],
            "user_id": row[2],
            "salle_id": row[3],
            "date": row[4].isoformat(),
            "heure": row[5].strftime("%H:%M")
        })
    return jsonify({"error": "Not found"}), 404

@app.route('/reservations', methods=['POST'])
def create():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reservations (titre, user_id, salle_id, date, heure)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (data['titre'], data['user_id'], data['salle_id'], data['date'], data['heure']))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    event = {
        "id": new_id,
        "titre": data['titre'],
        "user_id": data['user_id'],
        "salle_id": data['salle_id'],
        "date": data['date'],
        "heure": data['heure']
    }
    producer.send('reservation-events', event)
    producer.flush()

    return jsonify(event), 201

@app.route('/reservations/<int:id>', methods=['PUT'])
@require_role("Admin")
def update(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE reservations
        SET titre = %s, user_id = %s, salle_id = %s, date = %s, heure = %s
        WHERE id = %s;
    """, (data['titre'], data['user_id'], data['salle_id'], data['date'], data['heure'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Reservation updated"})

@app.route('/reservations/<int:id>', methods=['DELETE'])
@require_role("Admin")
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reservations WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Reservation deleted"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5003)


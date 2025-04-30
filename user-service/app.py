import psycopg2
from flask import Flask, jsonify, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
from functools import wraps

# Charger .env
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# OAuth Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'}
)

# Connexion PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host="user-db",
        database="users",
        user="postgres",
        password="postgres"
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            poste TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Employe'
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Middleware RBAC
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

# Auth routes
@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def authorized():
    token = google.authorize_access_token()
    if token is None:
        return jsonify({"error": "Authorization failed"}), 400
    user_info = google.get('userinfo').json()

    role = "Admin" if user_info['email'] == 'balaazikhouloud@gmail.com' else "Employe"
    session['user'] = {
        "name": user_info['name'],
        "email": user_info['email'],
        "role": role
    }

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = %s;", (user_info['email'],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (name, poste, email, role)
            VALUES (%s, %s, %s, %s)
        """, (user_info['name'], "Employé", user_info['email'], role))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/profile')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(session['user'])

# 🔐 Promotion d’un employé en Admin (accessible uniquement à Khouloud)
@app.route('/promote/<email>', methods=['POST'])
def promote_user(email):
    if 'user' not in session or session['user']['email'] != 'balaazikhouloud@gmail.com':
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = 'Admin' WHERE email = %s;", (email,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"{email} promu en Admin ✅"})

# API Utilisateur
@app.route('/')
def home():
    return jsonify({"message": "User service is running 👤"})

@app.route('/users', methods=['GET'])
@require_role("Admin")
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    users = [{"id": r[0], "name": r[1], "poste": r[2], "email": r[3], "role": r[4]} for r in rows]
    return jsonify(users)

@app.route('/users/<int:id>', methods=['GET'])
@require_role("Admin")
def get_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s;", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1], "poste": row[2], "email": row[3], "role": row[4]})
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
@require_role("Admin")
def create_user():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (name, poste, email, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (data['name'], data['poste'], data['email'], data.get('role', 'Employe')))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id}), 201

@app.route('/users/<int:id>', methods=['PUT'])
@require_role("Admin")
def update_user(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET name = %s, poste = %s, email = %s, role = %s
        WHERE id = %s;
    """, (data['name'], data['poste'], data['email'], data.get('role', 'Employe'), id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User updated"})

@app.route('/users/<int:id>', methods=['DELETE'])
@require_role("Admin")
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User deleted"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)


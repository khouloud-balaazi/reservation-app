from flask import Flask, jsonify, request

app = Flask(__name__)

# Simule une liste de réservations
reservations = [
    {"id": 1, "user_id": 1, "salle_id": 2, "date": "2024-04-15", "heure": "10:00"},
    {"id": 2, "user_id": 2, "salle_id": 1, "date": "2024-04-16", "heure": "14:00"}
]

@app.route('/reservations', methods=['GET'])
def get_reservations():
    return jsonify(reservations)

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    new_res = {
        "id": len(reservations) + 1,
        "user_id": data.get("user_id"),
        "salle_id": data.get("salle_id"),
        "date": data.get("date"),
        "heure": data.get("heure"),
        "titre": data.get("titre") 
    }
    reservations.append(new_res)
    return jsonify(new_res), 201

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Reservation service is running 📅"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)

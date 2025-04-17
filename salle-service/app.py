from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/salles', methods=['GET'])
def get_salles():
    salles = [
        {"id": 1, "nom": "Salle Alpha", "capacite": 10},
        {"id": 2, "nom": "Salle Beta", "capacite": 20}
    ]
    return jsonify(salles)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Salle service is running 🏢"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

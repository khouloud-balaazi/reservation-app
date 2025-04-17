from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    return jsonify(users)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "User service is running 🚀"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

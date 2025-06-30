from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

# Connexion MongoDB Atlas - remplace Admin:Admin par ton user et password
client = MongoClient("mongodb+srv://buveusechall95:Admin@cluster0.fjbpo5e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


db = client.apocal_db
collection = db.your_collection_name  # change ce nom par ta collection réelle

@app.route('/api/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {'_id': 0}))  # récupère tous les docs sans _id Mongo
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def add_data():
    new_data = request.json
    collection.insert_one(new_data)
    return jsonify({"message": "Donnée ajoutée"}), 201

if __name__ == '__main__':
    app.run(debug=True)

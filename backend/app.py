import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def extract_text_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def query_groq(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    snippet = text[:7000]  # limite pour tokenisation

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant intelligent qui synthétise des documents professionnels. "
                    "Réponds uniquement avec un JSON strict au format suivant : "
                    '{ "summary": "string", "keyPoints": ["string", "string"], "actions": ["string", "string"] }'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Voici un texte extrait d'un document :\n\n{snippet}\n\n"
                    "Merci de fournir un résumé clair, les points clés, et des actions à suivre au format JSON strict."
                ),
            },
        ],
        "temperature": 0.3,
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()
    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nom de fichier invalide"}), 400

    try:
        text = extract_text_from_pdf(file.stream)
        llm_response = query_groq(text)

        # Tenter de parser la réponse JSON stricte
        try:
            summary_json = json.loads(llm_response)
        except json.JSONDecodeError:
            return jsonify({"error": "La réponse LLM n'est pas un JSON valide", "raw_response": llm_response}), 500

        return jsonify(summary_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

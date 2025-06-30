from flask import Blueprint, request, jsonify
from pdf_utils import extract_text_from_pdf
from llm_summary import summarize_text
from mongo import db

api = Blueprint('api', __name__)

@api.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    text = extract_text_from_pdf(file)
    summary = summarize_text(text)

    # Sauvegarde dans MongoDB
    doc = {
        "filename": file.filename,
        "summary": summary
    }
    db.summaries.insert_one(doc)

    return jsonify({"summary": summary})

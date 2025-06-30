import os
import json
import tempfile
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.utils import secure_filename
import pdfplumber
from bson import ObjectId

from database import (
    create_user,
    authenticate_user,
    insert_document,
    get_document,
    list_documents,
)
from summarizer import generate_summary  # <‑‑ abstraction layer for HF


load_dotenv()
UPLOAD_DIR = tempfile.gettempdir()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60  # 1 hour
jwt = JWTManager(app)


# Helpers


def extract_text(pdf_path: str, max_pages: int = 30) -> str:
    """Extract raw text from the first `max_pages` of a PDF."""
    text_chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:max_pages]:
            text_chunks.append(page.extract_text() or "")
    return "\n".join(text_chunks)


# Auth endpoints


@app.post("/auth/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    success, msg = create_user(email, password)
    if not success:
        return jsonify({"error": msg}), 400
    return jsonify({"message": "user created"}), 201


@app.post("/auth/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = authenticate_user(email, password)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(identity=str(user["_id"]))
    return jsonify({"access_token": access_token})


# Summarization & documents


@app.post("/summarize")
@jwt_required()
def summarize():
    if "file" not in request.files:
        return jsonify({"error": "file field missing"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename or f"upload_{uuid4().hex}.pdf")
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    text = extract_text(file_path, max_pages=30)
    if not text.strip():
        return jsonify({"error": "PDF appears empty"}), 400

    # Call Hugging Face via summarizer abstraction
    content = generate_summary(text)

    # Persist to DB
    user_id = ObjectId(get_jwt_identity())
    doc = {
        "user_id": user_id,
        "filename": filename,
        "summary": content.get("summary", ""),
        "important_points": content.get("important_points", []),
        "created_at": datetime.utcnow(),
    }
    doc_id = insert_document(doc)

    return jsonify({"id": str(doc_id), **content}), 201


@app.get("/documents/<doc_id>")
@jwt_required()
def get_doc(doc_id):
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return jsonify({"error": "invalid id"}), 400

    doc = get_document(oid)
    if not doc or str(doc.get("user_id")) != get_jwt_identity():
        return jsonify({"error": "not found"}), 404

    return jsonify(
        {
            "id": str(doc["_id"]),
            "summary": doc["summary"],
            "important_points": doc["important_points"],
            "filename": doc["filename"],
            "created_at": doc["created_at"].isoformat() + "Z",
        }
    )


@app.get("/documents")
@jwt_required()
def list_docs():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    user_oid = ObjectId(get_jwt_identity())
    docs = list_documents(user_oid, page, limit)
    payload = [
        {
            "id": str(d["_id"]),
            "filename": d["filename"],
            "created_at": d["created_at"].isoformat() + "Z",
        }
        for d in docs
    ]
    return jsonify(payload)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
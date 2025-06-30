import os
import json
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise RuntimeError(
        "HF_API_KEY env var required (create one at https://huggingface.co/settings/tokens)"
    )

BASE_URL = "https://api-inference.huggingface.co/models"
MODEL_NAME = os.getenv("LLM_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json",
}


def _call_hf(prompt: str) -> str:
    """Low‑level POST to the HF inference endpoint; returns raw generated text."""
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": 0.2},
    }
    url = f"{BASE_URL}/{MODEL_NAME}"
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=180)

    if resp.status_code != 200:
        raise RuntimeError(
            f"HuggingFace API error {resp.status_code}: {resp.text[:200]}..."
        )

    data = resp.json()
    # HF returns either a list[dict] or dict depending on model
    if isinstance(data, list):
        return data[0].get("generated_text") or data[0].get("text", "")
    if isinstance(data, dict):
        return data.get("generated_text") or data.get("text", "")
    return str(data)


def generate_summary(text: str) -> dict:
    """Generate summary & important points, returning dict even if JSON parse fails."""
    prompt = (
        "Vous êtes un assistant de conformité. Fournis STRICTEMENT le JSON suivant :\n"
        '{"summary": "<3 phrases max>", "important_points": ["<pt1>", "<pt2>", ...]}\n\n'
        f"Document :\n{text[:12000]}"
    )

    raw = _call_hf(prompt)
    try:
        return json.loads(raw)
    except Exception:
        return {"summary": raw, "important_points": []}

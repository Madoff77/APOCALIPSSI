import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...")  # Remplace ici

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui résume des documents PDF."},
            {"role": "user", "content": text[:3000]}  # limite de tokens
        ]
    )
    return response.choices[0].message.content

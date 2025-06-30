const axios = require('axios');
require('dotenv').config();

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_MODEL = process.env.GROQ_MODEL || 'mistral-7b-32k';

async function summarizeText(text) {
  const response = await axios.post(
    'https://api.groq.com/openai/v1/chat/completions',
    {
      model: GROQ_MODEL,
      messages: [
        {
          role: 'system',
          content: 'Tu es un assistant juridique spécialisé dans la synthèse de documents réglementaires.',
        },
        {
          role: 'user',
          content: `Voici un document :\n\n${text}\n\nRésume-le en 5 points clés, puis suggère des actions concrètes.`,
        },
      ],
    },
    {
      headers: {
        Authorization: `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data.choices[0].message.content;
}

module.exports = { summarizeText };

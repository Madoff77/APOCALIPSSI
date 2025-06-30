require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());

// Stockage temporaire des fichiers uploadés en mémoire
const upload = multer({ storage: multer.memoryStorage() });

// Route racine simple
app.get('/', (req, res) => {
  res.send('Bienvenue sur l’API ComplySummarize IA 🚀');
});

// Route pour uploader un PDF et extraire le texte
app.post('/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Fichier PDF manquant' });
    }
    const dataBuffer = req.file.buffer;
    const data = await pdfParse(dataBuffer);
    res.json({ text: data.text });
  } catch (err) {
    res.status(500).json({ error: 'Erreur lors de l\'extraction du texte PDF' });
  }
});

// Route pour résumer un texte via Groq API
app.post('/summarize', async (req, res) => {
  const { text } = req.body;
  if (!text) return res.status(400).json({ error: 'Le champ texte est requis' });

  try {
    const response = await axios.post(
      'https://api.groq.ai/v1/generate', // vérifier l’URL officielle de Groq si besoin
      {
        prompt: `Résume ce texte de façon claire et structurée :\n\n${text}`,
        max_tokens: 300,
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
          'Content-Type': 'application/json',
        },
      }
    );

    const summary = response.data.choices?.[0]?.text || 'Résumé non disponible';
    res.json({ summary });
  } catch (error) {
    console.error(error.response?.data || error.message);
    res.status(500).json({ error: 'Erreur lors de la génération du résumé' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`✅ Serveur lancé sur http://localhost:${PORT}`);
});

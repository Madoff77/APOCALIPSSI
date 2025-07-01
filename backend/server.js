const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const fileUpload = require('express-fileupload');
const pdfParse = require('pdf-parse');
const dotenv = require('dotenv');
const summarizeRouter = require('./routes/summarize');

dotenv.config(); // 🔐 Chargement du fichier .env

const app = express();
const PORT = 5000;

// Middlewares
app.use(cors());
app.use(express.json());
app.use(fileUpload());

// Connexion à MongoDB via variable d’environnement
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('✅ Connexion à MongoDB réussie'))
.catch((err) => console.error('❌ Erreur de connexion à MongoDB :', err));

// Route de base
app.get('/', (req, res) => {
  res.send('Bienvenue sur l’API ComplySummarize IA 🚀');
});

// Routes
app.use('/api/summarize', summarizeRouter);

// Lancement du serveur
app.listen(PORT, () => {
  console.log(`✅ Serveur lancé sur http://localhost:${PORT}`);
});

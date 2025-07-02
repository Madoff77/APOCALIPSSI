import { useState, useCallback } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import FileUploader from './components/FileUploader';
import LoadingSpinner from './components/LoadingSpinner';
import ResultCard from './components/ResultCard';
import Footer from './components/Footer';
import AuthModal from './components/AuthModal';
import { AnalysisResult, UploadState, AnalysisHistory } from './types';
import { useAuth } from './contexts/AuthContext';
import { apiService } from './services/api';

function AppContent() {
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  
  const { user, addAnalysis } = useAuth();

  const handleRequestLogin = useCallback(() => {
    setAuthMode('login');
    setShowAuthModal(true);
  }, []);

  const handleFileUpload = useCallback(async (file: File) => {
    setUploadState('uploading');
    setError(null);
    setFileName(file.name);

    try {
      const response = await apiService.uploadAndAnalyze(file);
      
      if (response.success && response.data) {
        setResult(response.data);
        setUploadState('success');
        
        // Actualiser l'historique si l'utilisateur est connecté
        if (user) {
          await addAnalysis({
            fileName: file.name,
            summary: response.data.summary,
            keyPoints: response.data.keyPoints,
            actions: response.data.actions,
          });
        }
      } else {
        throw new Error(response.error?.message || 'Échec de l\'analyse du document');
      }
    } catch (err: any) {
      console.error('Erreur lors de l\'upload:', err);
      setError(err.message || 'Une erreur est survenue lors de l\'analyse du document');
      setUploadState('error');
    }
  }, [user, addAnalysis]);

  const handleStartOver = useCallback(() => {
    setUploadState('idle');
    setResult(null);
    setError(null);
    setFileName('');
  }, []);

  const handleViewAnalysis = useCallback((analysis: AnalysisHistory) => {
    setResult({
      summary: analysis.summary,
      keyPoints: analysis.keyPoints,
      actions: analysis.actions,
    });
    setFileName(analysis.fileName);
    setUploadState('success');
  }, []);

  const handleGoHome = useCallback(() => {
    setUploadState('idle');
    setResult(null);
    setError(null);
    setFileName('');
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors duration-200">
      <Navigation onViewAnalysis={handleViewAnalysis} onGoHome={handleGoHome} />
      
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {uploadState === 'idle' && (
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                Analyse de documents alimentée par l'IA
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                Téléchargez vos documents PDF et obtenez instantanément des résumés, des insights clés 
                et des recommandations exploitables grâce à une technologie IA avancée.
              </p>
            </div>
          )}

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-8 transition-colors duration-200">
            {uploadState === 'idle' && (
              <FileUploader
                onFileUpload={handleFileUpload}
                isUploading={false}
                error={error ?? undefined}
                onRequestLogin={handleRequestLogin}
              />
            )}

            {uploadState === 'uploading' && (
              <LoadingSpinner message="Analyse de votre document avec l'IA..." />
            )}

            {uploadState === 'success' && result && (
              <div>
                <div className="flex justify-between items-center mb-8">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Résultats de l'analyse
                  </h2>
                  <div className="flex space-x-3">
                    <button
                      onClick={handleGoHome}
                      className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
                    >
                      Retour à l'accueil
                    </button>
                    <button
                      onClick={handleStartOver}
                      className="bg-gray-500 hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
                    >
                      Analyser un autre document
                    </button>
                  </div>
                </div>
                <ResultCard result={result} fileName={fileName} />
              </div>
            )}

            {uploadState === 'error' && (
              <div className="text-center py-12">
                <div className="text-red-500 dark:text-red-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Échec de l'analyse</h3>
                <p className="text-gray-600 dark:text-gray-300 mb-6">{error}</p>
                <button
                  onClick={handleStartOver}
                  className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors duration-200"
                >
                  Réessayer
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
      
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
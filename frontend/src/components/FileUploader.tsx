import React, { useCallback, useState } from 'react';
import { Upload, FileText, AlertCircle, Lock } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface FileUploaderProps {
  onFileUpload: (file: File) => void;
  isUploading: boolean;
  error?: string;
  onRequestLogin?: () => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ 
  onFileUpload, 
  isUploading, 
  error,
  onRequestLogin
}) => {
  const { user } = useAuth();
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (!user) {
      onRequestLogin?.();
      return;
    }
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === 'application/pdf');
    
    if (pdfFile) {
      onFileUpload(pdfFile);
    }
  }, [onFileUpload, user, onRequestLogin]);

  const handleZoneClick = useCallback((e: React.MouseEvent) => {
    if (!user) {
      e.preventDefault();
      onRequestLogin?.();
    }
  }, [user, onRequestLogin]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (!user) {
      e.preventDefault();
      onRequestLogin?.();
      return;
    }
    
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      onFileUpload(file);
    }
  }, [onFileUpload, user, onRequestLogin]);

  return (
    <div className="max-w-2xl mx-auto">
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300
          ${isDragOver 
            ? 'border-blue-400 dark:border-blue-500 bg-blue-50 dark:bg-blue-950/30' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-950/20'
          }
          ${isUploading ? 'pointer-events-none opacity-60' : ''}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleZoneClick}
      >
        {user && (
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
        )}
        
        <div className="flex flex-col items-center space-y-4">
          <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full">
            {isUploading ? (
              <Upload className="w-8 h-8 text-blue-500 dark:text-blue-400 animate-pulse" />
            ) : !user ? (
              <Lock className="w-8 h-8 text-orange-500 dark:text-orange-400" />
            ) : (
              <FileText className="w-8 h-8 text-blue-500 dark:text-blue-400" />
            )}
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {isUploading 
                ? 'Téléchargement en cours...' 
                : !user 
                  ? 'Connexion requise' 
                  : 'Téléchargez votre document PDF'
              }
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {!user 
                ? 'Connectez-vous pour analyser vos documents PDF avec l\'IA'
                : 'Glissez-déposez votre PDF ici, ou cliquez pour parcourir'
              }
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {!user 
                ? 'Vos analyses seront sauvegardées dans votre historique'
                : 'Taille maximale : 10 Mo • Format PDF uniquement'
              }
            </p>
          </div>
          
          {!isUploading && (
            <button
              type="button"
              onClick={!user ? onRequestLogin : undefined}
              className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors duration-200 font-medium"
            >
              {!user ? 'Se connecter' : 'Choisir un fichier'}
            </button>
          )}
        </div>
      </div>
      
      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-400" />
            <p className="text-red-700 dark:text-red-300 font-medium">Échec du téléchargement</p>
          </div>
          <p className="text-red-600 dark:text-red-400 mt-1">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
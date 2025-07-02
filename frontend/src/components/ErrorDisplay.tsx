import React from 'react';
import { AlertCircle, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { ApiError } from '../types';

interface ErrorDisplayProps {
  error: ApiError;
  onRetry?: () => void;
  className?: string;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry, className = '' }) => {
  const getErrorIcon = () => {
    if (error.message.toLowerCase().includes('réseau') || 
        error.message.toLowerCase().includes('serveur')) {
      return <WifiOff className="w-8 h-8 text-red-500 dark:text-red-400" />;
    }
    return <AlertCircle className="w-8 h-8 text-red-500 dark:text-red-400" />;
  };

  const getErrorTitle = () => {
    if (error.code === 'NETWORK_ERROR') return 'Problème de connexion';
    if (error.code === 'UNAUTHORIZED') return 'Accès non autorisé';
    if (error.code === 'FORBIDDEN') return 'Accès interdit';
    if (error.code === 'NOT_FOUND') return 'Ressource introuvable';
    if (error.code === 'SERVER_ERROR') return 'Erreur du serveur';
    return 'Une erreur est survenue';
  };

  const getErrorDescription = () => {
    if (error.message.toLowerCase().includes('réseau')) {
      return 'Vérifiez votre connexion internet et réessayez.';
    }
    if (error.code === 'UNAUTHORIZED') {
      return 'Veuillez vous reconnecter à votre compte.';
    }
    return error.message;
  };

  return (
    <div className={`bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-6 ${className}`}>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          {getErrorIcon()}
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
            {getErrorTitle()}
          </h3>
          <p className="text-red-700 dark:text-red-300 mb-4">
            {getErrorDescription()}
          </p>
          
          {error.details && (
            <details className="mb-4">
              <summary className="cursor-pointer text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200">
                Détails techniques
              </summary>
              <pre className="mt-2 text-xs text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/50 p-2 rounded overflow-auto">
                {JSON.stringify(error.details, null, 2)}
              </pre>
            </details>
          )}
          
          {onRetry && (
            <button
              onClick={onRetry}
              className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800 text-white px-4 py-2 rounded-lg transition-colors duration-200"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Réessayer</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay; 
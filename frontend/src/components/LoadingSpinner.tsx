import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Traitement de votre document en cours..." 
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <Loader2 className="w-12 h-12 text-blue-500 dark:text-blue-400 animate-spin" />
      </div>
      <p className="mt-4 text-gray-600 dark:text-gray-300 text-lg">{message}</p>
      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
        Cela peut prendre quelques instants...
      </p>
    </div>
  );
};

export default LoadingSpinner;
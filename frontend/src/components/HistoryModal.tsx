import React from 'react';
import { X, FileText, Calendar, Download, Eye } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { AnalysisHistory } from '../types';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onViewAnalysis: (analysis: AnalysisHistory) => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({ isOpen, onClose, onViewAnalysis }) => {
  const { analysisHistory } = useAuth();

  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Historique des analyses
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {analysisHistory.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Aucune analyse trouvée
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                Vous n'avez pas encore analysé de documents. Commencez par télécharger un PDF !
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {analysisHistory.map((analysis) => (
                <div
                  key={analysis.id}
                  className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-6 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow duration-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="bg-blue-100 dark:bg-blue-900/50 p-2 rounded-lg">
                          <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {analysis.fileName}
                          </h3>
                          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(analysis.uploadDate)}</span>
                          </div>
                        </div>
                      </div>
                      
                      <p className="text-gray-700 dark:text-gray-300 text-sm line-clamp-3 mb-4">
                        {analysis.summary}
                      </p>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
                        <span>{analysis.keyPoints.length} points clés</span>
                        <span>•</span>
                        <span>{analysis.actions.length} actions recommandées</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => {
                          onViewAnalysis(analysis);
                          onClose();
                        }}
                        className="p-2 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
                        title="Voir l'analyse"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;
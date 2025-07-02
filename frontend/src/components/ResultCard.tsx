import React from 'react';
import { FileText, Key, CheckSquare, Download } from 'lucide-react';
import { AnalysisResult } from '../types';

interface ResultCardProps {
  result: AnalysisResult;
  fileName: string;
}

const ResultCard: React.FC<ResultCardProps> = ({ result, fileName }) => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* En-tête */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-green-100 dark:bg-green-900/50 p-2 rounded-lg">
              <FileText className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Analyse terminée
              </h2>
              <p className="text-gray-600 dark:text-gray-300">{fileName}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Section Résumé */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-200">
        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-blue-100 dark:bg-blue-900/50 p-2 rounded-lg">
            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Résumé</h3>
        </div>
        <div className="prose prose-gray dark:prose-invert max-w-none">
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{result.summary}</p>
        </div>
      </div>

      {/* Section Points clés */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-200">
        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-teal-100 dark:bg-teal-900/50 p-2 rounded-lg">
            <Key className="w-5 h-5 text-teal-600 dark:text-teal-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Points clés</h3>
        </div>
        <ul className="space-y-3">
          {result.keyPoints.map((point, index) => (
            <li key={index} className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-teal-500 dark:bg-teal-400 rounded-full mt-2 flex-shrink-0" />
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{point}</p>
            </li>
          ))}
        </ul>
      </div>

      {/* Section Actions recommandées */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-200">
        <div className="flex items-center space-x-3 mb-4">
          <div className="bg-orange-100 dark:bg-orange-900/50 p-2 rounded-lg">
            <CheckSquare className="w-5 h-5 text-orange-600 dark:text-orange-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Actions recommandées</h3>
        </div>
        <div className="space-y-3">
          {result.actions.map((action, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div className="w-2 h-2 bg-orange-500 dark:bg-orange-400 rounded-full mt-2 flex-shrink-0" />
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                {action}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultCard;
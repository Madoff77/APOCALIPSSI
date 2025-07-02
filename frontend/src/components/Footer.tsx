import React from 'react';
import { Mail, Shield, HelpCircle } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-16 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            ComplySummarize IA
          </h3>
          <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Analyse intelligente de documents alimentée par l'IA. Transformez des PDF complexes 
            en insights exploitables grâce à notre technologie de résumé avancée.
          </p>
        </div>
        
        <div className="border-t border-gray-200 dark:border-gray-700 pt-8 mt-8">
          <p className="text-center text-gray-500 dark:text-gray-400 text-sm">
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
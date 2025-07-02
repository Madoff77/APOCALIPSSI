import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AnalysisHistory } from '../types';
import { apiService } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName: string, lastName: string) => Promise<void>;
  logout: (redirectToHome?: () => void) => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
  analysisHistory: AnalysisHistory[];
  addAnalysis: (analysis: Omit<AnalysisHistory, 'id' | 'uploadDate'>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          const response = await apiService.verifyToken();
          if (response.success && response.data) {
            setUser(response.data);
            
            // Charger l'historique d'analyse
            const historyResponse = await apiService.getAnalysisHistory();
            if (historyResponse.success && historyResponse.data) {
              setAnalysisHistory(historyResponse.data);
            }
          } else {
            // Token invalide, le supprimer
            localStorage.removeItem('token');
          }
        } catch (error) {
          console.error('Erreur lors de la vérification du token:', error);
          localStorage.removeItem('token');
        }
      } else {
        // Pas de token, essayer de charger l'historique public
        try {
          const historyResponse = await apiService.getAnalysisHistory();
          if (historyResponse.success && historyResponse.data) {
            setAnalysisHistory(historyResponse.data);
          }
        } catch (error) {
          console.log('Historique non disponible:', error);
        }
      }
      
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    
    try {
      const response = await apiService.login({ email, password });
      
      if (response.success && response.data) {
        const { user, token } = response.data;
        setUser(user);
        localStorage.setItem('token', token);
        
        // Charger l'historique d'analyse
        const historyResponse = await apiService.getAnalysisHistory();
        if (historyResponse.success && historyResponse.data) {
          setAnalysisHistory(historyResponse.data);
        }
      } else {
        throw new Error(response.error?.message || 'Échec de la connexion');
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, firstName: string, lastName: string) => {
    setIsLoading(true);
    
    try {
      const response = await apiService.register({ email, password, firstName, lastName });
      
      if (response.success && response.data) {
        const { user, token } = response.data;
        setUser(user);
        localStorage.setItem('token', token);
        setAnalysisHistory([]); // Nouvel utilisateur, historique vide
      } else {
        throw new Error(response.error?.message || 'Échec de l\'inscription');
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (redirectToHome?: () => void) => {
    setUser(null);
    localStorage.removeItem('token');
    setAnalysisHistory([]);
    
    // Rediriger vers l'accueil si la fonction est fournie
    if (redirectToHome) {
      redirectToHome();
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    if (!user) return;
    
    setIsLoading(true);
    
    try {
      const response = await apiService.updateProfile(data);
      
      if (response.success && response.data) {
        setUser(response.data);
      } else {
        throw new Error(response.error?.message || 'Échec de la mise à jour du profil');
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const addAnalysis = async (_analysis: Omit<AnalysisHistory, 'id' | 'uploadDate'>) => {
    // Recharger l'historique depuis l'API après une nouvelle analyse
    try {
      const response = await apiService.getAnalysisHistory();
      if (response.success && response.data) {
        setAnalysisHistory(response.data);
      }
    } catch (error) {
      console.log('Impossible de recharger l\'historique:', error);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      login,
      register,
      logout,
      updateProfile,
      analysisHistory,
      addAnalysis,
    }}>
      {children}
    </AuthContext.Provider>
  );
};
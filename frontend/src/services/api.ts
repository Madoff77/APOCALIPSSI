import { 
  AuthResponse, 
  LoginRequest, 
  RegisterRequest, 
  User, 
  AnalysisResult,
  AnalysisHistory,
  ApiResponse,
  ApiError 
} from '../types';

import { appConfig } from '../config/env';

const API_BASE_URL = appConfig.apiBaseUrl;

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const data = await response.json();
      
      if (!response.ok) {
        return {
          success: false,
          error: {
            message: data.error || data.message || 'Une erreur est survenue',
            code: data.code,
            details: data.details
          }
        };
      }

      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: {
          message: 'Erreur de communication avec le serveur'
        }
      };
    }
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(credentials),
    });

    return this.handleResponse<AuthResponse>(response);
  }

  async register(userData: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(userData),
    });

    return this.handleResponse<AuthResponse>(response);
  }

  async verifyToken(): Promise<ApiResponse<User>> {
    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<User>(response);
  }

  async updateProfile(userData: Partial<User>): Promise<ApiResponse<User>> {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(userData),
    });

    return this.handleResponse<User>(response);
  }

  // Analysis endpoints
  async uploadAndAnalyze(file: File): Promise<ApiResponse<AnalysisResult>> {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    const headers: HeadersInit = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/analysis/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return this.handleResponse<AnalysisResult>(response);
  }

  async getAnalysisHistory(): Promise<ApiResponse<AnalysisHistory[]>> {
    const response = await fetch(`${API_BASE_URL}/analysis/history`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<AnalysisHistory[]>(response);
  }

  async deleteAnalysis(analysisId: string): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<void>(response);
  }
}

export const apiService = new ApiService();
export default apiService; 
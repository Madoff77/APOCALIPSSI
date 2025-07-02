export interface AnalysisResult {
  summary: string;
  keyPoints: string[];
  actions: string[];
}

export interface UploadResponse {
  success: boolean;
  result?: AnalysisResult;
  error?: string;
}

export type UploadState = 'idle' | 'uploading' | 'success' | 'error';

// Types pour l'authentification
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  createdAt: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface AnalysisHistory {
  id: string;
  fileName: string;
  uploadDate: string;
  summary: string;
  keyPoints: string[];
  actions: string[];
}

// Types pour les erreurs API
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

// Types pour les réponses API génériques
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  success: boolean;
}
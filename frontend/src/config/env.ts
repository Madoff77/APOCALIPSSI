interface AppConfig {
  apiBaseUrl: string;
  environment: 'development' | 'production' | 'test';
}

function validateEnv(): AppConfig {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
  const environment = import.meta.env.VITE_APP_ENV || 'development';

  if (!apiBaseUrl) {
    console.warn(
      '⚠️  VITE_API_BASE_URL non définie. Utilisation de l\'URL par défaut: http://localhost:5000/api'
    );
  }

  if (!['development', 'production', 'test'].includes(environment)) {
    console.warn(
      `⚠️  VITE_APP_ENV invalide: "${environment}". Utilisation de "development" par défaut.`
    );
  }

  return {
    apiBaseUrl: apiBaseUrl || 'http://localhost:5000/api',
    environment: ['development', 'production', 'test'].includes(environment) 
      ? environment as 'development' | 'production' | 'test'
      : 'development',
  };
}

export const appConfig = validateEnv();

// Log de la configuration en développement
if (appConfig.environment === 'development') {
  console.log('🔧 Configuration de l\'application:', {
    apiBaseUrl: appConfig.apiBaseUrl,
    environment: appConfig.environment,
  });
} 
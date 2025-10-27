// API Configuration
const isDevelopment = import.meta.env.DEV;

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  DETECT: `${API_BASE_URL}/api/detect`,
  DETECT_VIDEO: `${API_BASE_URL}/api/detect/video`,
  DETECTIONS: `${API_BASE_URL}/api/detections`,
  STATS: `${API_BASE_URL}/api/stats`,
};

console.log('Environment:', isDevelopment ? 'Development' : 'Production');
console.log('API Base URL:', API_BASE_URL);
console.log('Socket URL:', SOCKET_URL);

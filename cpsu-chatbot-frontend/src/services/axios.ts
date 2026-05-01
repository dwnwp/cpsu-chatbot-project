import axios from 'axios';
import { useAuthStore } from '@/stores/useAuthStore';

// สร้าง Axios Instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_DOMAIN || '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore();
      authStore.isAuthenticated = false;
      
      if (globalThis.location.pathname !== '/') {
        globalThis.location.href = '/'; 
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
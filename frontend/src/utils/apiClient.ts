import { useStore } from '../store/useStore';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = useStore.getState().token;
  
  // Preserve existing headers and only add Authorization
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // If the body is FormData, don't set Content-Type — the browser
  // needs to set it automatically with the correct multipart boundary.
  if (options.body instanceof FormData) {
    headers.delete('Content-Type');
  }

  return fetch(url, {
    ...options,
    headers,
  });
};

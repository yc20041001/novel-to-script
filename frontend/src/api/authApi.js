import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const authClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 10000,
});

export async function login(username, password) {
  const response = await authClient.post('/api/auth/login', { username, password });
  return response.data;
}

export async function checkAuth() {
  const response = await authClient.get('/api/auth/me');
  return response.data;
}

export async function logout() {
  const response = await authClient.post('/api/auth/logout');
  return response.data;
}

export { API_BASE_URL };

import axios from 'axios';
import { API_BASE_URL } from './config';

const authClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 10000,
});

export async function getCaptcha() {
  const response = await authClient.get('/api/auth/captcha');
  return response.data;
}

export async function login(username, password, captchaId, captchaCode) {
  const response = await authClient.post('/api/auth/login', {
    username,
    password,
    captcha_id: captchaId,
    captcha_code: captchaCode,
  });
  return response.data;
}

export async function register(username, password, displayName, captchaId, captchaCode) {
  const response = await authClient.post('/api/auth/register', {
    username,
    password,
    display_name: displayName || undefined,
    captcha_id: captchaId,
    captcha_code: captchaCode,
  });
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

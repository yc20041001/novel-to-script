import axios from 'axios';
import { API_BASE_URL } from './scriptApi';

const adminClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 30000,
});

export async function fetchAdminStats() {
  const response = await adminClient.get('/api/admin/stats');
  return response.data;
}

export async function fetchAdminUsers() {
  const response = await adminClient.get('/api/admin/users');
  return response.data;
}

export async function updateAdminUser(userId, patch) {
  const response = await adminClient.patch(`/api/admin/users/${userId}`, patch);
  return response.data;
}

export async function fetchAdminGenerations(limit = 50) {
  const response = await adminClient.get('/api/admin/generations', {
    params: { limit },
  });
  return response.data;
}

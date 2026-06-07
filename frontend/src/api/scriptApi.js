import axios from 'axios';

const DEFAULT_API_BASE_URL =
  typeof window === 'undefined'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}:8000`;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;

const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 120000,
});

export async function generateScript(chapters, options) {
  const payload = { chapters };
  if (options) {
    payload.options = options;
  }
  const response = await client.post('/api/generate', payload);
  return response.data;
}

export async function fetchSchema() {
  const response = await client.get('/api/schema');
  return response.data;
}

export async function validateYaml(yamlText) {
  const response = await client.post('/api/validate-yaml', { yaml: yamlText });
  return response.data;
}

export { API_BASE_URL };

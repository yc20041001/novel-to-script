import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
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


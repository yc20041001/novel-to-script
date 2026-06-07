function getDefaultApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }

  const { hostname, protocol } = window.location;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:8000`;
  }

  return 'http://localhost:8000';
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || getDefaultApiBaseUrl();

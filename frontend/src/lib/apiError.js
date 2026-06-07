export function formatApiDetail(detail) {
  if (!detail) {
    return '';
  }
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map(formatApiDetail).filter(Boolean).join('；');
  }
  if (typeof detail === 'object') {
    const field = Array.isArray(detail.loc) ? detail.loc.join('.') : '';
    const message = detail.msg || detail.message || JSON.stringify(detail);
    return field ? `${field}: ${message}` : message;
  }
  return String(detail);
}

export function getApiErrorMessage(error, fallback) {
  return formatApiDetail(error?.response?.data?.detail) || fallback;
}

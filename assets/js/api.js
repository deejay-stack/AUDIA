// Same-origin API client. Authentication failures never fall back to demo access.
let csrf = '';
export async function api(path, options = {}) {
  const headers = {...options.headers};
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';
  if (options.method && !['GET', 'HEAD'].includes(options.method)) headers['X-CSRF-Token'] = csrf;
  let response;
  try {
    response = await fetch(`/api${path}`, {...options, headers, credentials: 'same-origin',
      body: options.body === undefined ? undefined : JSON.stringify(options.body)});
  } catch {
    throw new Error('Unable to reach AUDIA. Check your connection and try again.');
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/auth/')) {
      window.dispatchEvent(new Event('audia:unauthorized'));
    }
    const error = new Error(data.error || 'We could not complete that request. Please try again.');
    error.status = response.status;
    throw error;
  }
  if (data.csrf_token) csrf = data.csrf_token;
  return data;
}

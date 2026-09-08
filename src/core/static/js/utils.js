export function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content ?? '';
}

export async function fetchWithCsrf(url, options = {}) {
  const method = (options.method ?? 'GET').toUpperCase();
  const mutating = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
  const headers = new Headers(options.headers ?? {});

  if (mutating) {
    headers.set('X-CSRFToken', getCsrfToken());
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
  }

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`${method} ${url} → ${response.status}: ${text.slice(0, 200)}`);
  }
  return response;
}

export async function postJson(url, data) {
  const response = await fetchWithCsrf(url, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
}

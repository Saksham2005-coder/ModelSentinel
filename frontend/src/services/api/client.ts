export function getApiBaseUrl(): string {
  // If explicitly injected via Vite environment variable and is an absolute URL
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.startsWith('http')) {
    return envUrl.replace(/\/+$/, '');
  }

  // If running in browser on Railway production or any public host:
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname.includes('railway.app') || (hostname !== 'localhost' && hostname !== '127.0.0.1' && hostname !== '0.0.0.0')) {
      return 'https://backend-production-cca4.up.railway.app/api/v1';
    }
  }

  // Local development fallback
  return envUrl || '/api/v1';
}

export const API_BASE_URL = getApiBaseUrl();

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown, message: string) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const baseUrl = getApiBaseUrl();
  // Ensure clean joining of endpoint
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;
  
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  
  headers.set('Bypass-Tunnel-Reminder', 'true');
  
  const token = localStorage.getItem('modelsentinel_token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (netErr: unknown) {
    const msg = netErr instanceof Error ? netErr.message : 'Network request failed';
    throw new ApiError(0, { detail: msg }, msg);
  }

  const contentType = response.headers.get('content-type') || '';

  // Intercept HTML responses from SPA index.html or web servers
  if (contentType.includes('text/html')) {
    await response.text();
    // Do not attempt response.json() on HTML
    throw new ApiError(
      response.status === 200 ? 404 : response.status,
      { detail: `API endpoint returned HTML instead of JSON: ${cleanEndpoint}` },
      `API endpoint returned HTML instead of JSON: ${cleanEndpoint}`
    );
  }

  if (!response.ok) {
    let data;
    try {
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        data = { detail: text || response.statusText };
      }
    } catch {
      data = { detail: response.statusText };
    }
    
    // FastAPI usually returns { detail: "Error message" }
    const errorMessage = data?.detail || response.statusText || 'An unexpected API error occurred';
    throw new ApiError(response.status, data, errorMessage);
  }

  if (response.status === 204) {
    return {} as T;
  }

  try {
    return await response.json();
  } catch {
    throw new ApiError(
      response.status,
      { detail: 'Invalid JSON response from server' },
      'Invalid JSON response from server'
    );
  }
}


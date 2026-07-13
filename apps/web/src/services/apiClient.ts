const DEFAULT_TIMEOUT_MS = 30000;

export interface ApiErrorShape {
  message: string;
  status?: number;
  details?: unknown;
}

class ApiError extends Error {
  status?: number;
  details?: unknown;

  constructor(message: string, init?: { status?: number; details?: unknown }) {
    super(message);
    this.name = "ApiError";
    this.status = init?.status;
    this.details = init?.details;
  }
}

function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL ?? "/api/v1";
}

function buildUrl(path: string) {
  const baseUrl = getApiBaseUrl().replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  try {
    const response = await fetch(buildUrl(path), {
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {})
      },
      ...init,
      signal: controller.signal
    });

    const rawText = await response.text();
    let payload: unknown = null;

    if (rawText) {
      try {
        payload = JSON.parse(rawText);
      } catch {
        payload = rawText;
      }
    }

    if (!response.ok) {
      const message =
        typeof payload === "object" && payload !== null && "message" in payload && typeof (payload as { message?: unknown }).message === "string"
          ? (payload as { message: string }).message
          : `Request failed with status ${response.status}`;

      throw new ApiError(message, {
        status: response.status,
        details: payload
      });
    }

    return payload as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("The request timed out.");
    }

    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError("An unexpected error occurred.", { details: error });
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  return requestJson<T>(path, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function putJson<T>(path: string, body: unknown): Promise<T> {
  return requestJson<T>(path, {
    method: "PUT",
    body: JSON.stringify(body)
  });
}

export async function getJson<T>(path: string): Promise<T> {
  return requestJson<T>(path, { method: "GET" });
}

export { ApiError };

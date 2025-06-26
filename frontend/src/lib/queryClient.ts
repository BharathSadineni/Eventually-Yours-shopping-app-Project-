import { QueryClient } from "@tanstack/react-query";

/**
 * Singleton QueryClient instance for React Query
 */
export const queryClient = new QueryClient();

const BACKEND_BASE_URL = "https://eventually-yours-shopping-app-backend.onrender.com";

/**
 * Helper for making API requests.
 * @param method HTTP method (GET, POST, etc.)
 * @param url API endpoint (relative to /api)
 * @param body Optional request body (object, NOT string or FormData)
 * @param options Optional fetch options (headers, etc.)
 *
 * DO NOT pass JSON.stringify(body) or FormData as the body. Always pass a plain object.
 * Example: apiRequest('POST', '/api/user-info', { age: 25 })
 */
export async function apiRequest(
  method: string,
  url: string,
  body?: any,
  options: RequestInit = {}
) {
  // Runtime check: Only allow plain objects or undefined/null as body
  if (
    body !== undefined &&
    (typeof body === "string" ||
      (typeof window !== "undefined" && body instanceof window.FormData))
  ) {
    throw new Error(
      "[apiRequest] Invalid body: Do NOT pass JSON.stringify or FormData. Pass a plain object."
    );
  }

  const fetchOptions: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  if (body !== undefined) {
    fetchOptions.body = JSON.stringify(body);
  }

  // Use absolute URL in production, relative in development (for proxy)
  const isRelativeApi = url.startsWith("/api");
  const fullUrl =
    isRelativeApi && import.meta.env.PROD
      ? BACKEND_BASE_URL + url
      : url;

  const response = await fetch(fullUrl, fetchOptions);

  if (!response.ok) {
    // Try to parse error message from response
    let errorMsg = `API request failed: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.message || errorMsg;
    } catch {
      // ignore JSON parse error
    }
    throw new Error(errorMsg);
  }

  return response;
} 
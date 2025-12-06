/**
 * API Client for Pac-Man Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1';

// Token storage keys
const ACCESS_TOKEN_KEY = 'pacman_access_token';
const REFRESH_TOKEN_KEY = 'pacman_refresh_token';

// Token management
export const getAccessToken = (): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
};

export const getRefreshToken = (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setTokens = (accessToken: string, refreshToken: string): void => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

export const clearTokens = (): void => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// API error type
export interface ApiError {
    code: string;
    message: string;
    details?: Record<string, unknown>;
}

// Generic API response handler
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
            code: 'UNKNOWN_ERROR',
            message: response.statusText,
        }));
        throw error;
    }
    return response.json();
}

// API request helper
export async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = getAccessToken();

    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
    };

    if (token) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    // Handle 401 - try to refresh token
    if (response.status === 401 && token) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            // Retry with new token
            const newToken = getAccessToken();
            (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
            const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers,
            });
            return handleResponse<T>(retryResponse);
        }
    }

    return handleResponse<T>(response);
}

// Token refresh
async function tryRefreshToken(): Promise<boolean> {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        clearTokens();
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refreshToken }),
        });

        if (!response.ok) {
            clearTokens();
            return false;
        }

        const data = await response.json();
        setTokens(data.accessToken, data.refreshToken);
        return true;
    } catch {
        clearTokens();
        return false;
    }
}

// Health check
export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
    return apiRequest('/health');
}

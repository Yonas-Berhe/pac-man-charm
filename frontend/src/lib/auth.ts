/**
 * Authentication API services
 */

import { apiRequest, setTokens, clearTokens, getAccessToken } from './api';

// Types
export interface User {
    id: string;
    username: string;
    email: string;
    avatar_url: string | null;
    high_score: number;
    games_played: number;
    created_at: string;
    updated_at: string;
}

export interface AuthResponse {
    user: User;
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
}

export interface RegisterData {
    username: string;
    email: string;
    password: string;
}

export interface LoginData {
    email: string;
    password: string;
}

// Auth functions
export async function register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiRequest<AuthResponse>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
    });

    setTokens(response.accessToken, response.refreshToken);
    return response;
}

export async function login(data: LoginData): Promise<AuthResponse> {
    const response = await apiRequest<AuthResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(data),
    });

    setTokens(response.accessToken, response.refreshToken);
    return response;
}

export async function logout(): Promise<void> {
    try {
        await apiRequest('/auth/logout', { method: 'POST' });
    } finally {
        clearTokens();
    }
}

export async function getCurrentUser(): Promise<User> {
    return apiRequest<User>('/users/me');
}

export function isAuthenticated(): boolean {
    return !!getAccessToken();
}

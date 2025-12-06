/**
 * Game API services
 */

import { apiRequest } from './api';

// Types
export interface GameSession {
    id: string;
    userId: string;
    status: 'active' | 'completed' | 'abandoned';
    startedAt: string;
    endedAt: string | null;
    finalScore: number | null;
    result: 'won' | 'lost' | null;
}

export interface EndGameData {
    finalScore: number;
    result: 'won' | 'lost';
    dotsCollected?: number;
    powerDotsCollected?: number;
    ghostsEaten?: number;
    livesRemaining?: number;
    duration?: number;
}

export interface GameResult {
    game: GameSession;
    isHighScore: boolean;
    previousHighScore: number | null;
    newRank: number | null;
}

export interface GameHistoryResponse {
    games: GameSession[];
    total: number;
}

// Game functions
export async function startGameSession(): Promise<GameSession> {
    return apiRequest<GameSession>('/games', { method: 'POST' });
}

export async function endGameSession(gameId: string, data: EndGameData): Promise<GameResult> {
    return apiRequest<GameResult>(`/games/${gameId}/end`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function getGameHistory(limit = 10, offset = 0): Promise<GameHistoryResponse> {
    return apiRequest<GameHistoryResponse>(`/games?limit=${limit}&offset=${offset}`);
}

export async function getGameSession(gameId: string): Promise<GameSession> {
    return apiRequest<GameSession>(`/games/${gameId}`);
}

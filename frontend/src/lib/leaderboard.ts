/**
 * Leaderboard API services
 */

import { apiRequest } from './api';

// Types
export interface PublicUser {
    id: string;
    username: string;
    avatar_url: string | null;
    high_score: number;
    games_played: number;
}

export interface LeaderboardEntry {
    rank: number;
    user: PublicUser;
    score: number;
    achievedAt: string;
}

export interface LeaderboardResponse {
    entries: LeaderboardEntry[];
    total: number;
    period: 'all_time' | 'monthly' | 'weekly' | 'daily';
}

export interface UserRank {
    rank: number | null;
    score: number;
    percentile: number;
    period: string;
}

export interface UserStats {
    userId: string;
    gamesPlayed: number;
    gamesWon: number;
    gamesLost: number;
    winRate: number;
    highScore: number;
    averageScore: number;
    totalDotsCollected: number;
    totalGhostsEaten: number;
    totalPlayTime: number;
}

// Leaderboard functions
export async function getLeaderboard(
    period: 'all_time' | 'monthly' | 'weekly' | 'daily' = 'all_time',
    limit = 10,
    offset = 0
): Promise<LeaderboardResponse> {
    return apiRequest<LeaderboardResponse>(
        `/leaderboard?period=${period}&limit=${limit}&offset=${offset}`
    );
}

export async function getMyRank(
    period: 'all_time' | 'monthly' | 'weekly' | 'daily' = 'all_time'
): Promise<UserRank> {
    return apiRequest<UserRank>(`/leaderboard/me?period=${period}`);
}

export async function getUserStats(userId: string): Promise<UserStats> {
    return apiRequest<UserStats>(`/users/${userId}/stats`);
}

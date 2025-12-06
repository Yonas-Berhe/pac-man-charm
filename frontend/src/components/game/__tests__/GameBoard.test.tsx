import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GameBoard } from '../GameBoard';
import { AuthProvider } from '@/contexts/AuthContext';

// Mock the API modules to prevent actual API calls
vi.mock('@/lib/api', () => ({
    getAccessToken: vi.fn(() => null),
    clearTokens: vi.fn(),
}));

vi.mock('@/lib/auth', () => ({
    getCurrentUser: vi.fn(),
    isAuthenticated: vi.fn(() => false),
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
}));

// Mock the useGameLogic hook
vi.mock('../useGameLogic', () => ({
    useGameLogic: vi.fn(() => ({
        gameState: {
            pacmanPosition: { x: 9, y: 15 },
            pacmanDirection: null,
            ghosts: [
                { id: 'ghost-0', position: { x: 8, y: 9 }, color: 'red', direction: null, isScared: false },
                { id: 'ghost-1', position: { x: 9, y: 9 }, color: 'pink', direction: null, isScared: false },
                { id: 'ghost-2', position: { x: 10, y: 9 }, color: 'cyan', direction: null, isScared: false },
                { id: 'ghost-3', position: { x: 9, y: 8 }, color: 'orange', direction: null, isScared: false },
            ],
            dots: [{ x: 1, y: 1 }, { x: 2, y: 1 }],
            powerDots: [{ x: 1, y: 2 }],
            score: 0,
            lives: 3,
            gameStatus: 'idle' as const,
            dotsCollectedCount: 0,
            powerDotsCollectedCount: 0,
            ghostsEatenCount: 0,
        },
        startGame: vi.fn(),
    })),
}));

// Import the mock after defining it
import { useGameLogic } from '../useGameLogic';

// Helper to render with providers
const renderWithProviders = (ui: React.ReactElement) => {
    return render(
        <AuthProvider>
            {ui}
        </AuthProvider>
    );
};

describe('GameBoard', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders the game title', () => {
        renderWithProviders(<GameBoard />);
        expect(screen.getByText('PAC-MAN')).toBeInTheDocument();
    });

    it('displays the initial score as 000000', () => {
        renderWithProviders(<GameBoard />);
        expect(screen.getByText(/SCORE: 000000/)).toBeInTheDocument();
    });

    it('shows START GAME button when game is idle', () => {
        renderWithProviders(<GameBoard />);
        expect(screen.getByText('START GAME')).toBeInTheDocument();
    });

    it('calls startGame when START GAME button is clicked', () => {
        const mockStartGame = vi.fn();
        vi.mocked(useGameLogic).mockReturnValue({
            gameState: {
                pacmanPosition: { x: 9, y: 15 },
                pacmanDirection: null,
                ghosts: [],
                dots: [],
                powerDots: [],
                score: 0,
                lives: 3,
                gameStatus: 'idle',
                dotsCollectedCount: 0,
                powerDotsCollectedCount: 0,
                ghostsEatenCount: 0,
            },
            startGame: mockStartGame,
        });

        renderWithProviders(<GameBoard />);
        fireEvent.click(screen.getByText('START GAME'));
        expect(mockStartGame).toHaveBeenCalled();
    });

    it('displays the correct number of lives', () => {
        renderWithProviders(<GameBoard />);
        const liveIcons = document.querySelectorAll('.life-icon');
        expect(liveIcons).toHaveLength(3);
    });

    it('shows YOU WIN message when game is won', () => {
        vi.mocked(useGameLogic).mockReturnValue({
            gameState: {
                pacmanPosition: { x: 9, y: 15 },
                pacmanDirection: null,
                ghosts: [],
                dots: [],
                powerDots: [],
                score: 1000,
                lives: 3,
                gameStatus: 'won',
                dotsCollectedCount: 0,
                powerDotsCollectedCount: 0,
                ghostsEatenCount: 0,
            },
            startGame: vi.fn(),
        });

        renderWithProviders(<GameBoard />);
        expect(screen.getByText('YOU WIN!')).toBeInTheDocument();
        expect(screen.getByText('PLAY AGAIN')).toBeInTheDocument();
    });

    it('shows GAME OVER message when game is lost', () => {
        vi.mocked(useGameLogic).mockReturnValue({
            gameState: {
                pacmanPosition: { x: 9, y: 15 },
                pacmanDirection: null,
                ghosts: [],
                dots: [],
                powerDots: [],
                score: 500,
                lives: 0,
                gameStatus: 'lost',
                dotsCollectedCount: 0,
                powerDotsCollectedCount: 0,
                ghostsEatenCount: 0,
            },
            startGame: vi.fn(),
        });

        renderWithProviders(<GameBoard />);
        expect(screen.getByText('GAME OVER')).toBeInTheDocument();
        expect(screen.getByText('TRY AGAIN')).toBeInTheDocument();
    });

    it('displays instructions text', () => {
        // Reset to idle state to ensure instruction overlay is shown
        vi.mocked(useGameLogic).mockReturnValue({
            gameState: {
                pacmanPosition: { x: 9, y: 15 },
                pacmanDirection: null,
                ghosts: [],
                dots: [],
                powerDots: [],
                score: 0,
                lives: 3,
                gameStatus: 'idle',
                dotsCollectedCount: 0,
                powerDotsCollectedCount: 0,
                ghostsEatenCount: 0,
            },
            startGame: vi.fn(),
        });

        renderWithProviders(<GameBoard />);
        expect(screen.getByText('Use Arrow Keys or WASD')).toBeInTheDocument();
        expect(screen.getByText('Eat all dots to win • Collect power dots to eat ghosts!')).toBeInTheDocument();
    });
});

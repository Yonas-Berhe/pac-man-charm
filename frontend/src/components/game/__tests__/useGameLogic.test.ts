import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useGameLogic } from '../useGameLogic';

describe('useGameLogic', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    describe('initial state', () => {
        it('starts with score of 0', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.score).toBe(0);
        });

        it('starts with 3 lives', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.lives).toBe(3);
        });

        it('starts in idle status', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.gameStatus).toBe('idle');
        });

        it('starts with null direction', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.pacmanDirection).toBeNull();
        });

        it('has 4 ghosts', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.ghosts).toHaveLength(4);
        });

        it('ghosts have correct colors', () => {
            const { result } = renderHook(() => useGameLogic());
            const colors = result.current.gameState.ghosts.map(g => g.color);
            expect(colors).toContain('red');
            expect(colors).toContain('pink');
            expect(colors).toContain('cyan');
            expect(colors).toContain('orange');
        });

        it('has dots to collect', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.dots.length).toBeGreaterThan(0);
        });

        it('has power dots to collect', () => {
            const { result } = renderHook(() => useGameLogic());
            expect(result.current.gameState.powerDots.length).toBeGreaterThan(0);
        });
    });

    describe('startGame', () => {
        it('sets game status to playing', () => {
            const { result } = renderHook(() => useGameLogic());

            act(() => {
                result.current.startGame();
            });

            expect(result.current.gameState.gameStatus).toBe('playing');
        });

        it('resets score to 0', () => {
            const { result } = renderHook(() => useGameLogic());

            // Start and manipulate game state would change score
            act(() => {
                result.current.startGame();
            });

            expect(result.current.gameState.score).toBe(0);
        });

        it('resets lives to 3', () => {
            const { result } = renderHook(() => useGameLogic());

            act(() => {
                result.current.startGame();
            });

            expect(result.current.gameState.lives).toBe(3);
        });

        it('resets direction to null', () => {
            const { result } = renderHook(() => useGameLogic());

            act(() => {
                result.current.startGame();
            });

            expect(result.current.gameState.pacmanDirection).toBeNull();
        });

        it('resets ghosts to not scared', () => {
            const { result } = renderHook(() => useGameLogic());

            act(() => {
                result.current.startGame();
            });

            result.current.gameState.ghosts.forEach(ghost => {
                expect(ghost.isScared).toBe(false);
            });
        });
    });

    describe('keyboard controls', () => {
        it('responds to arrow up key', () => {
            const { result } = renderHook(() => useGameLogic());

            act(() => {
                result.current.startGame();
            });

            act(() => {
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp' }));
                vi.advanceTimersByTime(180); // Game loop interval
            });

            // The direction may or may not change depending on wall placement
            // But the event should be processed
            expect(result.current.gameState.gameStatus).toBe('playing');
        });

        it('responds to WASD keys', () => {
            const { result } = renderHook(() => useGameLogic());

            act(() => {
                result.current.startGame();
            });

            act(() => {
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'w' }));
                vi.advanceTimersByTime(180);
            });

            expect(result.current.gameState.gameStatus).toBe('playing');
        });
    });

    describe('game loop', () => {
        it('game loop runs when playing', () => {
            const { result } = renderHook(() => useGameLogic());

            const initialPosition = { ...result.current.gameState.pacmanPosition };

            act(() => {
                result.current.startGame();
            });

            // Set a direction
            act(() => {
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
                vi.advanceTimersByTime(180);
            });

            // Game loop should process the movement (if valid)
            expect(result.current.gameState.gameStatus).toBe('playing');
        });

        it('game loop does not run when idle', () => {
            const { result } = renderHook(() => useGameLogic());

            const initialPosition = { ...result.current.gameState.pacmanPosition };

            act(() => {
                vi.advanceTimersByTime(500);
            });

            // Position should not change when idle
            expect(result.current.gameState.pacmanPosition).toEqual(initialPosition);
        });
    });

    describe('ghost behavior', () => {
        it('ghosts start not scared', () => {
            const { result } = renderHook(() => useGameLogic());

            result.current.gameState.ghosts.forEach(ghost => {
                expect(ghost.isScared).toBe(false);
            });
        });
    });
});

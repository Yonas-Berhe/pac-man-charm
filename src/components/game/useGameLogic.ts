import { useState, useEffect, useCallback, useRef } from 'react';
import { Direction, Position, Ghost, GameState, MAZE_LAYOUT, CELL_SIZE } from './types';

const GHOST_COLORS: ('red' | 'pink' | 'cyan' | 'orange')[] = ['red', 'pink', 'cyan', 'orange'];

const getInitialDots = (): Position[] => {
  const dots: Position[] = [];
  MAZE_LAYOUT.forEach((row, y) => {
    row.forEach((cell, x) => {
      if (cell === 2) dots.push({ x, y });
    });
  });
  return dots;
};

const getInitialPowerDots = (): Position[] => {
  const powerDots: Position[] = [];
  MAZE_LAYOUT.forEach((row, y) => {
    row.forEach((cell, x) => {
      if (cell === 3) powerDots.push({ x, y });
    });
  });
  return powerDots;
};

const getPacmanSpawn = (): Position => {
  for (let y = 0; y < MAZE_LAYOUT.length; y++) {
    for (let x = 0; x < MAZE_LAYOUT[y].length; x++) {
      if (MAZE_LAYOUT[y][x] === 5) return { x, y };
    }
  }
  return { x: 9, y: 15 };
};

const getGhostSpawns = (): Position[] => {
  const spawns: Position[] = [];
  MAZE_LAYOUT.forEach((row, y) => {
    row.forEach((cell, x) => {
      if (cell === 4) spawns.push({ x, y });
    });
  });
  return spawns;
};

const canMove = (x: number, y: number): boolean => {
  if (x < 0 || x >= MAZE_LAYOUT[0].length || y < 0 || y >= MAZE_LAYOUT.length) {
    // Allow tunnel wrap
    if (y === 9 && (x < 0 || x >= MAZE_LAYOUT[0].length)) return true;
    return false;
  }
  return MAZE_LAYOUT[y][x] !== 1;
};

const getNextPosition = (pos: Position, dir: Direction): Position => {
  switch (dir) {
    case 'up': return { x: pos.x, y: pos.y - 1 };
    case 'down': return { x: pos.x, y: pos.y + 1 };
    case 'left': return { x: pos.x - 1, y: pos.y };
    case 'right': return { x: pos.x + 1, y: pos.y };
    default: return pos;
  }
};

const wrapPosition = (pos: Position): Position => {
  let { x, y } = pos;
  if (x < 0) x = MAZE_LAYOUT[0].length - 1;
  if (x >= MAZE_LAYOUT[0].length) x = 0;
  return { x, y };
};

export const useGameLogic = () => {
  const [gameState, setGameState] = useState<GameState>(() => ({
    pacmanPosition: getPacmanSpawn(),
    pacmanDirection: null,
    ghosts: getGhostSpawns().map((pos, i) => ({
      id: `ghost-${i}`,
      position: pos,
      color: GHOST_COLORS[i % GHOST_COLORS.length],
      direction: null,
      isScared: false,
    })),
    dots: getInitialDots(),
    powerDots: getInitialPowerDots(),
    score: 0,
    lives: 3,
    gameStatus: 'idle',
  }));

  const nextDirection = useRef<Direction>(null);
  const scaredTimer = useRef<NodeJS.Timeout | null>(null);

  const startGame = useCallback(() => {
    setGameState({
      pacmanPosition: getPacmanSpawn(),
      pacmanDirection: null,
      ghosts: getGhostSpawns().map((pos, i) => ({
        id: `ghost-${i}`,
        position: pos,
        color: GHOST_COLORS[i % GHOST_COLORS.length],
        direction: null,
        isScared: false,
      })),
      dots: getInitialDots(),
      powerDots: getInitialPowerDots(),
      score: 0,
      lives: 3,
      gameStatus: 'playing',
    });
    nextDirection.current = null;
  }, []);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const dirMap: Record<string, Direction> = {
      ArrowUp: 'up',
      ArrowDown: 'down',
      ArrowLeft: 'left',
      ArrowRight: 'right',
      w: 'up',
      s: 'down',
      a: 'left',
      d: 'right',
    };
    
    if (dirMap[e.key]) {
      e.preventDefault();
      nextDirection.current = dirMap[e.key];
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Game loop
  useEffect(() => {
    if (gameState.gameStatus !== 'playing') return;

    const gameLoop = setInterval(() => {
      setGameState(prev => {
        if (prev.gameStatus !== 'playing') return prev;

        // Move Pac-Man
        let newPacmanDir = prev.pacmanDirection;
        let newPacmanPos = prev.pacmanPosition;

        if (nextDirection.current) {
          const testPos = getNextPosition(prev.pacmanPosition, nextDirection.current);
          if (canMove(testPos.x, testPos.y)) {
            newPacmanDir = nextDirection.current;
          }
        }

        if (newPacmanDir) {
          const testPos = getNextPosition(prev.pacmanPosition, newPacmanDir);
          if (canMove(testPos.x, testPos.y)) {
            newPacmanPos = wrapPosition(testPos);
          }
        }

        // Check dot collection
        let newDots = prev.dots;
        let newPowerDots = prev.powerDots;
        let newScore = prev.score;
        let newGhosts = prev.ghosts;

        const dotIndex = newDots.findIndex(d => d.x === newPacmanPos.x && d.y === newPacmanPos.y);
        if (dotIndex !== -1) {
          newDots = newDots.filter((_, i) => i !== dotIndex);
          newScore += 10;
        }

        const powerDotIndex = newPowerDots.findIndex(d => d.x === newPacmanPos.x && d.y === newPacmanPos.y);
        if (powerDotIndex !== -1) {
          newPowerDots = newPowerDots.filter((_, i) => i !== powerDotIndex);
          newScore += 50;
          newGhosts = newGhosts.map(g => ({ ...g, isScared: true }));
          
          if (scaredTimer.current) clearTimeout(scaredTimer.current);
          scaredTimer.current = setTimeout(() => {
            setGameState(s => ({
              ...s,
              ghosts: s.ghosts.map(g => ({ ...g, isScared: false }))
            }));
          }, 7000);
        }

        // Move ghosts
        newGhosts = newGhosts.map(ghost => {
          const directions: Direction[] = ['up', 'down', 'left', 'right'];
          const validDirs = directions.filter(dir => {
            const testPos = getNextPosition(ghost.position, dir);
            return canMove(testPos.x, testPos.y);
          });

          // Simple AI: move towards/away from pacman
          let bestDir = ghost.direction;
          if (validDirs.length > 0) {
            if (ghost.isScared) {
              // Run away
              validDirs.sort((a, b) => {
                const posA = getNextPosition(ghost.position, a);
                const posB = getNextPosition(ghost.position, b);
                const distA = Math.abs(posA.x - newPacmanPos.x) + Math.abs(posA.y - newPacmanPos.y);
                const distB = Math.abs(posB.x - newPacmanPos.x) + Math.abs(posB.y - newPacmanPos.y);
                return distB - distA;
              });
            } else {
              // Chase (with some randomness)
              if (Math.random() > 0.3) {
                validDirs.sort((a, b) => {
                  const posA = getNextPosition(ghost.position, a);
                  const posB = getNextPosition(ghost.position, b);
                  const distA = Math.abs(posA.x - newPacmanPos.x) + Math.abs(posA.y - newPacmanPos.y);
                  const distB = Math.abs(posB.x - newPacmanPos.x) + Math.abs(posB.y - newPacmanPos.y);
                  return distA - distB;
                });
              }
            }
            bestDir = validDirs[0];
          }

          const newPos = bestDir ? wrapPosition(getNextPosition(ghost.position, bestDir)) : ghost.position;
          return { ...ghost, position: newPos, direction: bestDir };
        });

        // Check ghost collision
        let newLives = prev.lives;
        let newStatus: GameState['gameStatus'] = prev.gameStatus;

        for (const ghost of newGhosts) {
          if (ghost.position.x === newPacmanPos.x && ghost.position.y === newPacmanPos.y) {
            if (ghost.isScared) {
              // Eat ghost
              newScore += 200;
              ghost.position = getGhostSpawns()[0];
              ghost.isScared = false;
            } else {
              // Lose life
              newLives--;
              if (newLives <= 0) {
                newStatus = 'lost';
              } else {
                newPacmanPos = getPacmanSpawn();
                newPacmanDir = null;
                nextDirection.current = null;
              }
            }
          }
        }

        // Check win
        if (newDots.length === 0 && newPowerDots.length === 0) {
          newStatus = 'won';
        }

        return {
          ...prev,
          pacmanPosition: newPacmanPos,
          pacmanDirection: newPacmanDir,
          ghosts: newGhosts,
          dots: newDots,
          powerDots: newPowerDots,
          score: newScore,
          lives: newLives,
          gameStatus: newStatus,
        };
      });
    }, 180);

    return () => clearInterval(gameLoop);
  }, [gameState.gameStatus]);

  return { gameState, startGame };
};

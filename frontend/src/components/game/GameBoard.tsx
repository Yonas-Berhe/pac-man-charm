import { useState, useEffect, useRef } from 'react';
import { useGameLogic } from './useGameLogic';
import { Maze } from './Maze';
import { Pacman } from './Pacman';
import { Ghost } from './Ghost';
import { Dots } from './Dots';
import { Leaderboard } from './Leaderboard';
import { GameResultDialog } from './GameResultDialog';
import { CELL_SIZE, MAZE_WIDTH, MAZE_HEIGHT } from './types';
import { useAuth } from '@/contexts/AuthContext';
import { AuthModal } from '@/components/auth/AuthModal';
import { UserMenu } from '@/components/auth/UserMenu';
import { Button } from '@/components/ui/button';
import { startGameSession, endGameSession, GameResult } from '@/lib/games';
import { Trophy, LogIn } from 'lucide-react';

export const GameBoard = () => {
  const { gameState, startGame } = useGameLogic();
  const { user, isAuthenticated, refreshUser } = useAuth();

  // Modal states
  const [showAuth, setShowAuth] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [showResult, setShowResult] = useState(false);

  // Game session tracking
  const [currentGameId, setCurrentGameId] = useState<string | null>(null);
  const [gameResult, setGameResult] = useState<GameResult | null>(null);
  const gameStartTime = useRef<number>(0);
  const prevGameStatus = useRef(gameState.gameStatus);

  const boardWidth = MAZE_WIDTH * CELL_SIZE;
  const boardHeight = MAZE_HEIGHT * CELL_SIZE;

  // Track game start
  const handleStartGame = async () => {
    gameStartTime.current = Date.now();
    setGameResult(null);

    if (isAuthenticated) {
      try {
        const session = await startGameSession();
        setCurrentGameId(session.id);
      } catch (error) {
        console.error('Failed to start game session:', error);
      }
    }

    startGame();
  };

  // Track game end
  useEffect(() => {
    const wasPlaying = prevGameStatus.current === 'playing';
    const isEnded = gameState.gameStatus === 'won' || gameState.gameStatus === 'lost';

    if (wasPlaying && isEnded && isAuthenticated && currentGameId) {
      const duration = Math.floor((Date.now() - gameStartTime.current) / 1000);

      endGameSession(currentGameId, {
        finalScore: gameState.score,
        result: gameState.gameStatus as 'won' | 'lost',
        dotsCollected: gameState.dotsCollectedCount || 0,
        powerDotsCollected: gameState.powerDotsCollectedCount || 0,
        ghostsEaten: gameState.ghostsEatenCount || 0,
        livesRemaining: gameState.lives,
        duration,
      })
        .then((result) => {
          setGameResult(result);
          setShowResult(true);
          refreshUser(); // Update user stats
        })
        .catch((error) => {
          console.error('Failed to end game session:', error);
        });

      setCurrentGameId(null);
    }

    prevGameStatus.current = gameState.gameStatus;
  }, [gameState.gameStatus, gameState.score, gameState.lives, currentGameId, isAuthenticated, refreshUser, gameState.dotsCollectedCount, gameState.powerDotsCollectedCount, gameState.ghostsEatenCount]);

  const handlePlayAgain = () => {
    setShowResult(false);
    handleStartGame();
  };

  return (
    <div className="game-container">
      {/* Header with auth and leaderboard */}
      <div className="game-header">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowLeaderboard(true)}
          className="gap-2"
        >
          <Trophy className="h-4 w-4" />
          Leaderboard
        </Button>

        {isAuthenticated ? (
          <UserMenu />
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAuth(true)}
            className="gap-2"
          >
            <LogIn className="h-4 w-4" />
            Sign In
          </Button>
        )}
      </div>

      <h1 className="game-title">PAC-MAN</h1>

      <div className="score-display">
        SCORE: {gameState.score.toString().padStart(6, '0')}
        {user && (
          <span className="text-xs text-muted-foreground ml-4">
            HIGH: {user.high_score.toString().padStart(6, '0')}
          </span>
        )}
      </div>

      <div
        className="game-board"
        style={{ width: boardWidth, height: boardHeight }}
      >
        <Maze />
        <Dots dots={gameState.dots} powerDots={gameState.powerDots} />
        <Pacman
          position={gameState.pacmanPosition}
          direction={gameState.pacmanDirection}
        />
        {gameState.ghosts.map(ghost => (
          <Ghost key={ghost.id} ghost={ghost} />
        ))}

        {gameState.gameStatus === 'idle' && (
          <div className="game-over-overlay">
            <p className="text-primary text-sm mb-6">Use Arrow Keys or WASD</p>
            <button className="btn-play" onClick={handleStartGame}>
              START GAME
            </button>
            {!isAuthenticated && (
              <p className="text-muted-foreground text-xs mt-4">
                Sign in to save your scores!
              </p>
            )}
          </div>
        )}

        {gameState.gameStatus === 'won' && !showResult && (
          <div className="game-over-overlay">
            <p className="text-primary text-xl mb-4">YOU WIN!</p>
            <p className="text-secondary text-sm mb-6">Score: {gameState.score}</p>
            <button className="btn-play" onClick={handleStartGame}>
              PLAY AGAIN
            </button>
          </div>
        )}

        {gameState.gameStatus === 'lost' && !showResult && (
          <div className="game-over-overlay">
            <p className="text-destructive text-xl mb-4">GAME OVER</p>
            <p className="text-secondary text-sm mb-6">Score: {gameState.score}</p>
            <button className="btn-play" onClick={handleStartGame}>
              TRY AGAIN
            </button>
          </div>
        )}
      </div>

      <div className="lives-display">
        {Array.from({ length: gameState.lives }).map((_, i) => (
          <div key={i} className="life-icon" />
        ))}
      </div>

      <p className="text-muted-foreground text-xs mt-6">
        Eat all dots to win • Collect power dots to eat ghosts!
      </p>

      {/* Modals */}
      <AuthModal open={showAuth} onOpenChange={setShowAuth} />
      <Leaderboard open={showLeaderboard} onOpenChange={setShowLeaderboard} />
      <GameResultDialog
        open={showResult}
        onOpenChange={setShowResult}
        result={gameResult}
        gameStatus={gameState.gameStatus as 'won' | 'lost'}
        onPlayAgain={handlePlayAgain}
      />
    </div>
  );
};

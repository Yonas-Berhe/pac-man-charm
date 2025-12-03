import { useGameLogic } from './useGameLogic';
import { Maze } from './Maze';
import { Pacman } from './Pacman';
import { Ghost } from './Ghost';
import { Dots } from './Dots';
import { CELL_SIZE, MAZE_WIDTH, MAZE_HEIGHT } from './types';

export const GameBoard = () => {
  const { gameState, startGame } = useGameLogic();

  const boardWidth = MAZE_WIDTH * CELL_SIZE;
  const boardHeight = MAZE_HEIGHT * CELL_SIZE;

  return (
    <div className="game-container">
      <h1 className="game-title">PAC-MAN</h1>
      
      <div className="score-display">
        SCORE: {gameState.score.toString().padStart(6, '0')}
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
            <button className="btn-play" onClick={startGame}>
              START GAME
            </button>
          </div>
        )}

        {gameState.gameStatus === 'won' && (
          <div className="game-over-overlay">
            <p className="text-primary text-xl mb-4">YOU WIN!</p>
            <p className="text-secondary text-sm mb-6">Score: {gameState.score}</p>
            <button className="btn-play" onClick={startGame}>
              PLAY AGAIN
            </button>
          </div>
        )}

        {gameState.gameStatus === 'lost' && (
          <div className="game-over-overlay">
            <p className="text-destructive text-xl mb-4">GAME OVER</p>
            <p className="text-secondary text-sm mb-6">Score: {gameState.score}</p>
            <button className="btn-play" onClick={startGame}>
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
    </div>
  );
};

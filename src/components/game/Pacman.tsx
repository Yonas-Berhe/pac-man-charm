import { Position, Direction, CELL_SIZE } from './types';

interface PacmanProps {
  position: Position;
  direction: Direction;
}

export const Pacman = ({ position, direction }: PacmanProps) => {
  const rotation = {
    right: 0,
    down: 90,
    left: 180,
    up: 270,
  };

  return (
    <div
      className="pacman pacman-mouth"
      style={{
        left: position.x * CELL_SIZE + 2,
        top: position.y * CELL_SIZE + 2,
        width: CELL_SIZE - 4,
        height: CELL_SIZE - 4,
        transform: `rotate(${rotation[direction || 'right']}deg)`,
      }}
    />
  );
};

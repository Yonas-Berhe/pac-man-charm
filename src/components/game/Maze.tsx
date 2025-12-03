import { MAZE_LAYOUT, CELL_SIZE } from './types';

export const Maze = () => {
  const walls: JSX.Element[] = [];

  MAZE_LAYOUT.forEach((row, y) => {
    row.forEach((cell, x) => {
      if (cell === 1) {
        walls.push(
          <div
            key={`wall-${x}-${y}`}
            className="maze-wall"
            style={{
              left: x * CELL_SIZE,
              top: y * CELL_SIZE,
              width: CELL_SIZE,
              height: CELL_SIZE,
            }}
          />
        );
      }
    });
  });

  return <>{walls}</>;
};

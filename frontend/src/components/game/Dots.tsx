import { Position, CELL_SIZE } from './types';

interface DotsProps {
  dots: Position[];
  powerDots: Position[];
}

export const Dots = ({ dots, powerDots }: DotsProps) => {
  return (
    <>
      {dots.map((dot, i) => (
        <div
          key={`dot-${i}`}
          className="dot"
          style={{
            left: dot.x * CELL_SIZE + CELL_SIZE / 2 - 3,
            top: dot.y * CELL_SIZE + CELL_SIZE / 2 - 3,
            width: 6,
            height: 6,
          }}
        />
      ))}
      {powerDots.map((dot, i) => (
        <div
          key={`power-${i}`}
          className="power-dot"
          style={{
            left: dot.x * CELL_SIZE + CELL_SIZE / 2 - 6,
            top: dot.y * CELL_SIZE + CELL_SIZE / 2 - 6,
            width: 12,
            height: 12,
          }}
        />
      ))}
    </>
  );
};

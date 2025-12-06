import { Ghost as GhostType, CELL_SIZE } from './types';

interface GhostProps {
  ghost: GhostType;
}

export const Ghost = ({ ghost }: GhostProps) => {
  const size = CELL_SIZE - 4;

  return (
    <div
      className={`ghost ghost-${ghost.isScared ? 'scared' : ghost.color}`}
      style={{
        left: ghost.position.x * CELL_SIZE + 2,
        top: ghost.position.y * CELL_SIZE + 2,
        width: size,
        height: size,
      }}
    >
      <div
        className="ghost-body"
        style={{
          width: '100%',
          height: '80%',
          position: 'relative',
        }}
      >
        {/* Eyes */}
        <div
          style={{
            position: 'absolute',
            top: '30%',
            left: '20%',
            width: '25%',
            height: '30%',
            background: 'white',
            borderRadius: '50%',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: '30%',
              left: '30%',
              width: '40%',
              height: '40%',
              background: ghost.isScared ? 'white' : '#000',
              borderRadius: '50%',
            }}
          />
        </div>
        <div
          style={{
            position: 'absolute',
            top: '30%',
            right: '20%',
            width: '25%',
            height: '30%',
            background: 'white',
            borderRadius: '50%',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: '30%',
              left: '30%',
              width: '40%',
              height: '40%',
              background: ghost.isScared ? 'white' : '#000',
              borderRadius: '50%',
            }}
          />
        </div>
      </div>
      {/* Wavy bottom */}
      <svg
        viewBox="0 0 20 6"
        style={{
          width: '100%',
          height: '20%',
          position: 'absolute',
          bottom: 0,
        }}
      >
        <path
          d="M0,0 Q2.5,6 5,0 T10,0 T15,0 T20,0 L20,6 L0,6 Z"
          fill={`hsl(var(--ghost-${ghost.isScared ? 'scared' : ghost.color}))`}
        />
      </svg>
    </div>
  );
};

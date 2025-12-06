import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Pacman } from '../Pacman';

describe('Pacman', () => {
    it('renders at the correct position', () => {
        const { container } = render(<Pacman position={{ x: 5, y: 10 }} direction="right" />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toBeInTheDocument();
        // Position calculation: x * CELL_SIZE + 2 = 5 * 24 + 2 = 122
        expect(pacman).toHaveStyle({ left: '122px', top: '242px' });
    });

    it('rotates 0 degrees when facing right', () => {
        const { container } = render(<Pacman position={{ x: 0, y: 0 }} direction="right" />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toHaveStyle({ transform: 'rotate(0deg)' });
    });

    it('rotates 90 degrees when facing down', () => {
        const { container } = render(<Pacman position={{ x: 0, y: 0 }} direction="down" />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toHaveStyle({ transform: 'rotate(90deg)' });
    });

    it('rotates 180 degrees when facing left', () => {
        const { container } = render(<Pacman position={{ x: 0, y: 0 }} direction="left" />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toHaveStyle({ transform: 'rotate(180deg)' });
    });

    it('rotates 270 degrees when facing up', () => {
        const { container } = render(<Pacman position={{ x: 0, y: 0 }} direction="up" />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toHaveStyle({ transform: 'rotate(270deg)' });
    });

    it('defaults to right rotation when direction is null', () => {
        const { container } = render(<Pacman position={{ x: 0, y: 0 }} direction={null} />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toHaveStyle({ transform: 'rotate(0deg)' });
    });

    it('has the pacman-mouth class for animation', () => {
        const { container } = render(<Pacman position={{ x: 0, y: 0 }} direction="right" />);
        const pacman = container.querySelector('.pacman');

        expect(pacman).toHaveClass('pacman-mouth');
    });
});

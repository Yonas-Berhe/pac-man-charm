import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Ghost } from '../Ghost';

describe('Ghost', () => {
    const createGhost = (overrides = {}) => ({
        id: 'ghost-0',
        position: { x: 5, y: 10 },
        color: 'red' as const,
        direction: null,
        isScared: false,
        ...overrides,
    });

    it('renders at the correct position', () => {
        const ghost = createGhost();
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostEl = container.querySelector('.ghost');

        expect(ghostEl).toBeInTheDocument();
        // Position calculation: x * CELL_SIZE + 2 = 5 * 24 + 2 = 122
        expect(ghostEl).toHaveStyle({ left: '122px', top: '242px' });
    });

    it('has the correct color class for red ghost', () => {
        const ghost = createGhost({ color: 'red' });
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostEl = container.querySelector('.ghost');

        expect(ghostEl).toHaveClass('ghost-red');
    });

    it('has the correct color class for pink ghost', () => {
        const ghost = createGhost({ color: 'pink' });
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostEl = container.querySelector('.ghost');

        expect(ghostEl).toHaveClass('ghost-pink');
    });

    it('has the correct color class for cyan ghost', () => {
        const ghost = createGhost({ color: 'cyan' });
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostEl = container.querySelector('.ghost');

        expect(ghostEl).toHaveClass('ghost-cyan');
    });

    it('has the correct color class for orange ghost', () => {
        const ghost = createGhost({ color: 'orange' });
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostEl = container.querySelector('.ghost');

        expect(ghostEl).toHaveClass('ghost-orange');
    });

    it('has scared class when ghost is scared', () => {
        const ghost = createGhost({ isScared: true });
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostEl = container.querySelector('.ghost');

        expect(ghostEl).toHaveClass('ghost-scared');
        expect(ghostEl).not.toHaveClass('ghost-red');
    });

    it('renders eyes', () => {
        const ghost = createGhost();
        const { container } = render(<Ghost ghost={ghost} />);
        const ghostBody = container.querySelector('.ghost-body');

        expect(ghostBody).toBeInTheDocument();
        // Eyes are rendered as white background divs
        const eyeElements = ghostBody?.querySelectorAll('[style*="background: white"]');
        expect(eyeElements?.length).toBeGreaterThanOrEqual(2);
    });

    it('renders wavy bottom SVG', () => {
        const ghost = createGhost();
        const { container } = render(<Ghost ghost={ghost} />);
        const svg = container.querySelector('svg');

        expect(svg).toBeInTheDocument();
    });
});

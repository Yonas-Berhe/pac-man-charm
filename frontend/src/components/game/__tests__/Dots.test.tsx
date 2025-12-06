import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Dots } from '../Dots';

describe('Dots', () => {
    it('renders regular dots', () => {
        const dots = [
            { x: 1, y: 1 },
            { x: 2, y: 1 },
            { x: 3, y: 1 },
        ];
        const { container } = render(<Dots dots={dots} powerDots={[]} />);
        const dotElements = container.querySelectorAll('.dot');

        expect(dotElements).toHaveLength(3);
    });

    it('renders power dots', () => {
        const powerDots = [
            { x: 1, y: 2 },
            { x: 17, y: 2 },
        ];
        const { container } = render(<Dots dots={[]} powerDots={powerDots} />);
        const powerDotElements = container.querySelectorAll('.power-dot');

        expect(powerDotElements).toHaveLength(2);
    });

    it('renders both regular and power dots together', () => {
        const dots = [{ x: 1, y: 1 }];
        const powerDots = [{ x: 1, y: 2 }];
        const { container } = render(<Dots dots={dots} powerDots={powerDots} />);

        expect(container.querySelectorAll('.dot')).toHaveLength(1);
        expect(container.querySelectorAll('.power-dot')).toHaveLength(1);
    });

    it('renders empty when no dots provided', () => {
        const { container } = render(<Dots dots={[]} powerDots={[]} />);

        expect(container.querySelectorAll('.dot')).toHaveLength(0);
        expect(container.querySelectorAll('.power-dot')).toHaveLength(0);
    });

    it('positions regular dots correctly', () => {
        const dots = [{ x: 5, y: 10 }];
        const { container } = render(<Dots dots={dots} powerDots={[]} />);
        const dot = container.querySelector('.dot');

        // Position calculation: x * CELL_SIZE + CELL_SIZE / 2 - 3 = 5 * 24 + 12 - 3 = 129
        expect(dot).toHaveStyle({ left: '129px', top: '249px' });
    });

    it('positions power dots correctly', () => {
        const powerDots = [{ x: 5, y: 10 }];
        const { container } = render(<Dots dots={[]} powerDots={powerDots} />);
        const powerDot = container.querySelector('.power-dot');

        // Position calculation: x * CELL_SIZE + CELL_SIZE / 2 - 6 = 5 * 24 + 12 - 6 = 126
        expect(powerDot).toHaveStyle({ left: '126px', top: '246px' });
    });

    it('power dots are larger than regular dots', () => {
        const dots = [{ x: 1, y: 1 }];
        const powerDots = [{ x: 2, y: 2 }];
        const { container } = render(<Dots dots={dots} powerDots={powerDots} />);

        const dot = container.querySelector('.dot');
        const powerDot = container.querySelector('.power-dot');

        expect(dot).toHaveStyle({ width: '6px', height: '6px' });
        expect(powerDot).toHaveStyle({ width: '12px', height: '12px' });
    });
});

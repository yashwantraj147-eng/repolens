import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScoreCard } from '../components/ScoreCard';

describe('ScoreCard Component', () => {
  it('renders overall score and grade accurately', () => {
    const healthScore = {
      overall: 88,
      grade: 'A-',
      breakdown: {},
    };

    render(<ScoreCard healthScore={healthScore} />);

    expect(screen.getByText('88')).toBeInTheDocument();
    expect(screen.getByText('Out of 100')).toBeInTheDocument();
    expect(screen.getByText(/Grade A-/)).toBeInTheDocument();
    expect(screen.getByText(/Repository Health Score/i)).toBeInTheDocument();
  });

  it('renders nothing when healthScore is null', () => {
    const { container } = render(<ScoreCard healthScore={null} />);
    expect(container.firstChild).toBeNull();
  });
});


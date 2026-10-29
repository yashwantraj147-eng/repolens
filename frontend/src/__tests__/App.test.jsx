import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App Component', () => {
  it('renders landing page headline and features', () => {
    render(<App />);

    const brandElements = screen.getAllByText('RepoLens');
    expect(brandElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Instant architecture diagrams & health scores/i)).toBeInTheDocument();
    expect(screen.getByText('Mermaid Diagrams')).toBeInTheDocument();
    expect(screen.getByText('7-Point Health Score')).toBeInTheDocument();
  });
});

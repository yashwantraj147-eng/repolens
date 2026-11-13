import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock getRecentReports to avoid unhandled async updates
vi.mock('../utils/api', async () => {
  const actual = await vi.importActual('../utils/api');
  return {
    ...actual,
    getRecentReports: vi.fn().mockResolvedValue([]),
  };
});

describe('App Component', () => {
  it('renders landing page headline and features', async () => {
    await act(async () => {
      render(<App />);
    });

    const brandElements = screen.getAllByText('RepoLens');
    expect(brandElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Instant architecture diagrams & health scores/i)).toBeInTheDocument();
    expect(screen.getByText('Mermaid Diagrams')).toBeInTheDocument();
    expect(screen.getByText('7-Point Health Score')).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RepoInput } from '../components/RepoInput';

describe('RepoInput Component', () => {
  it('renders input field and sample buttons', () => {
    const handleAnalyze = vi.fn();
    render(<RepoInput onAnalyze={handleAnalyze} loading={false} />);

    const input = screen.getByPlaceholderText(/Paste public GitHub URL/i);
    expect(input).toBeInTheDocument();
    expect(screen.getByText('FastAPI')).toBeInTheDocument();
    expect(screen.getByText('Express')).toBeInTheDocument();
  });

  it('validates URL before submission', () => {
    const handleAnalyze = vi.fn();
    render(<RepoInput onAnalyze={handleAnalyze} loading={false} />);

    const input = screen.getByPlaceholderText(/Paste public GitHub URL/i);
    const submitBtn = screen.getByRole('button', { name: /Analyze/i });

    // Invalid url
    fireEvent.change(input, { target: { value: 'not-a-valid-github-url' } });
    fireEvent.click(submitBtn);

    expect(screen.getByText(/Please enter a valid GitHub URL/i)).toBeInTheDocument();
    expect(handleAnalyze).not.toHaveBeenCalled();
  });

  it('triggers onAnalyze when valid URL is submitted', () => {
    const handleAnalyze = vi.fn();
    render(<RepoInput onAnalyze={handleAnalyze} loading={false} />);

    const input = screen.getByPlaceholderText(/Paste public GitHub URL/i);
    const submitBtn = screen.getByRole('button', { name: /Analyze/i });

    fireEvent.change(input, { target: { value: 'https://github.com/fastapi/fastapi' } });
    fireEvent.click(submitBtn);

    expect(handleAnalyze).toHaveBeenCalledWith('https://github.com/fastapi/fastapi');
  });

  it('triggers onAnalyze when a sample pill is clicked', () => {
    const handleAnalyze = vi.fn();
    render(<RepoInput onAnalyze={handleAnalyze} loading={false} />);

    const sampleBtn = screen.getByText('FastAPI');
    fireEvent.click(sampleBtn);

    expect(handleAnalyze).toHaveBeenCalledWith('https://github.com/fastapi/fastapi');
  });
});


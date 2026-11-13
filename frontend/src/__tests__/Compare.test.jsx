import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CompareInput } from '../components/CompareInput';
import { ComparePage } from '../components/ComparePage';

describe('CompareInput Component', () => {
  it('renders both repo inputs and preset buttons', () => {
    render(<CompareInput onCompare={() => {}} loading={false} />);

    expect(screen.getByPlaceholderText('e.g. fastapi/fastapi')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g. pallets/flask')).toBeInTheDocument();
    expect(screen.getByText('FastAPI vs Flask')).toBeInTheDocument();
    expect(screen.getByText('Compare')).toBeInTheDocument();
  });

  it('validates empty inputs on submit', () => {
    render(<CompareInput onCompare={() => {}} loading={false} />);

    const submitBtn = screen.getByText('Compare');
    fireEvent.click(submitBtn);

    expect(screen.getByText('Please provide two repositories to compare.')).toBeInTheDocument();
  });

  it('triggers onCompare when preset is clicked', () => {
    const handleCompare = vi.fn();
    render(<CompareInput onCompare={handleCompare} loading={false} />);

    const presetBtn = screen.getByText('FastAPI vs Flask');
    fireEvent.click(presetBtn);

    expect(handleCompare).toHaveBeenCalledWith('fastapi/fastapi', 'pallets/flask');
  });
});

describe('ComparePage Component', () => {
  const mockCompareData = {
    repo_a: {
      report_id: 'rep_fastapi',
      repo: {
        owner: 'fastapi',
        name: 'fastapi',
        url: 'https://github.com/fastapi/fastapi',
        description: 'FastAPI framework',
        language: 'Python',
        stars: 70000,
        forks: 6000,
        open_issues: 500,
      },
      health_score: {
        overall: 88,
        grade: 'A-',
      },
    },
    repo_b: {
      report_id: 'rep_flask',
      repo: {
        owner: 'pallets',
        name: 'flask',
        url: 'https://github.com/pallets/flask',
        description: 'The Python micro framework',
        language: 'Python',
        stars: 65000,
        forks: 16000,
        open_issues: 10,
      },
      health_score: {
        overall: 80,
        grade: 'B+',
      },
    },
    comparison: {
      overall_winner: 'repo_a',
      score_diff: 8,
      verdict_summary: 'fastapi/fastapi takes the lead with an overall score of 88/100 vs 80/100 (+8).',
      categories: [
        {
          category: 'security_posture',
          name: 'Security & Supply Chain',
          score_a: 95,
          score_b: 60,
          winner: 'repo_a',
          diff: 35,
          details_a: 'CodeQL and Dependabot active',
          details_b: 'Missing Dependabot',
        },
      ],
      metrics: {
        stars_diff: 5000,
        forks_diff: -10000,
        open_issues_diff: 490,
        stars_winner: 'repo_a',
        forks_winner: 'repo_b',
      },
    },
  };

  it('renders winner badge, repo cards, and category matrix', () => {
    render(
      <ComparePage
        compareData={mockCompareData}
        onReset={() => {}}
        onSelectReport={() => {}}
      />
    );

    expect(screen.getByText('Head-to-Head Comparison')).toBeInTheDocument();
    expect(screen.getByText('fastapi/fastapi Leads (+8 pts)')).toBeInTheDocument();
    expect(screen.getByText('Security & Supply Chain')).toBeInTheDocument();
    expect(screen.getByText('fastapi (+35)')).toBeInTheDocument();
  });
});

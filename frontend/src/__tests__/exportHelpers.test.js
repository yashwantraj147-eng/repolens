import { describe, it, expect } from 'vitest';
import { generateMarkdownReport, generateContributingGuide } from '../utils/exportHelpers';

const mockReport = {
  report_id: 'rep_12345',
  created_at: '2026-10-30T00:00:00Z',
  repo: {
    owner: 'testowner',
    name: 'testrepo',
    url: 'https://github.com/testowner/testrepo',
    description: 'A test repository',
    language: 'Python',
    stars: 1250,
    forks: 340,
    open_issues: 12,
    license_name: 'MIT',
  },
  health_score: {
    overall_score: 92,
    grade: 'A',
    breakdown: {
      readme_quality: {
        name: 'README Quality',
        score: 18,
        max_score: 20,
        weight: 0.2,
        passed: true,
        reason: 'Comprehensive documentation',
      },
      test_coverage: {
        name: 'Test Coverage',
        score: 18,
        max_score: 20,
        weight: 0.2,
        passed: true,
        reason: 'High test suite density',
      },
    },
    recommendations: [
      {
        title: 'Add SECURITY.md',
        description: 'Provide vulnerability disclosure policy',
      },
    ],
  },
  summary: {
    one_line_summary: 'Fast full-stack test toolkit.',
    what_it_does: 'Provides automated testing utilities for distributed systems.',
    tech_stack: [
      { name: 'FastAPI', category: 'Backend', purpose: 'REST API' },
    ],
    standout_features: ['Sub-millisecond latency', 'Zero config'],
  },
  architecture_diagram: 'graph TD\n  ROOT --> SRC',
  onboarding_guide: {
    prerequisites: ['Python 3.11+', 'Docker'],
    setup_steps: [
      { title: 'Install dependencies', command: 'pip install -r requirements.txt' },
    ],
    run_command: 'python -m app.main',
    test_command: 'pytest',
  },
};

describe('exportHelpers', () => {
  describe('generateMarkdownReport', () => {
    it('generates a full markdown report with all key sections', () => {
      const md = generateMarkdownReport(mockReport);
      expect(md).toContain('# RepoLens Health & Architecture Audit: testowner/testrepo');
      expect(md).toContain('Health & Maintainability Score: 92/100 (Grade: A)');
      expect(md).toContain('README Quality');
      expect(md).toContain('Add SECURITY.md');
      expect(md).toContain('```mermaid');
      expect(md).toContain('graph TD');
      expect(md).toContain('pip install -r requirements.txt');
      expect(md).toContain('pytest');
      expect(md).toContain('/api/badge/testowner/testrepo.svg');
    });

    it('handles empty report gracefully', () => {
      expect(generateMarkdownReport(null)).toBe('');
      expect(generateMarkdownReport({})).toBe('');
    });
  });

  describe('generateContributingGuide', () => {
    it('generates a clean CONTRIBUTING.md guide with setup commands', () => {
      const md = generateContributingGuide(mockReport);
      expect(md).toContain('# Contributing to testrepo');
      expect(md).toContain('Python 3.11+');
      expect(md).toContain('git clone https://github.com/testowner/testrepo.git');
      expect(md).toContain('pip install -r requirements.txt');
      expect(md).toContain('pytest');
      expect(md).toContain('Pull Request Workflow');
    });

    it('handles null gracefully', () => {
      expect(generateContributingGuide(null)).toBe('');
    });
  });
});

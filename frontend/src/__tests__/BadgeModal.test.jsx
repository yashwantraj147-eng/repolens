import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BadgeModal } from '../components/BadgeModal';

const mockRepo = {
  owner: 'fastapi',
  name: 'fastapi',
};

const mockReport = {
  report_id: 'rep_fastapi123',
};

describe('BadgeModal Component', () => {
  it('does not render when isOpen is false', () => {
    const { container } = render(
      <BadgeModal
        isOpen={false}
        onClose={() => {}}
        repo={mockRepo}
        report={mockReport}
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders modal with live preview, styles, and snippet boxes when isOpen is true', () => {
    render(
      <BadgeModal
        isOpen={true}
        onClose={() => {}}
        repo={mockRepo}
        report={mockReport}
      />
    );

    expect(screen.getByText('Embed Health Badge')).toBeInTheDocument();
    expect(screen.getByText('Live Preview')).toBeInTheDocument();
    expect(screen.getByText('Flat (Default)')).toBeInTheDocument();
    expect(screen.getByText('Flat Square')).toBeInTheDocument();
    expect(screen.getByText('For The Badge')).toBeInTheDocument();

    const img = screen.getByAltText('RepoLens Health Badge');
    expect(img).toBeInTheDocument();
    expect(img.getAttribute('src')).toContain('/api/badge/fastapi/fastapi.svg?style=flat');
  });

  it('switches badge style when clicking style buttons', () => {
    render(
      <BadgeModal
        isOpen={true}
        onClose={() => {}}
        repo={mockRepo}
        report={mockReport}
      />
    );

    const forTheBadgeBtn = screen.getByText('For The Badge');
    fireEvent.click(forTheBadgeBtn);

    const img = screen.getByAltText('RepoLens Health Badge');
    expect(img.getAttribute('src')).toContain('style=for-the-badge');
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(
      <BadgeModal
        isOpen={true}
        onClose={handleClose}
        repo={mockRepo}
        report={mockReport}
      />
    );

    const doneBtn = screen.getByText('Done');
    fireEvent.click(doneBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

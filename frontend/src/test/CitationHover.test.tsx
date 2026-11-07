import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CitationHover } from '../components/CitationHover';
import { SourceItem } from '../types';

describe('CitationHover Component', () => {
  const mockSource: SourceItem = {
    id: 1,
    title: 'BitDelta India Regulatory Review',
    url: 'https://example.com/bitdelta-compliance',
    domain: 'example.com',
    source_type: 'web',
    retrieved_at: new Date().toISOString(),
    supported_claims: ['FIU-IND registered entity operating compliant orderbook']
  };

  it('renders citation index bracket', () => {
    render(<CitationHover id={1} source={mockSource} />);
    expect(screen.getByText('[1]')).toBeInTheDocument();
  });

  it('reveals popover with evidence on hover', () => {
    render(<CitationHover id={1} source={mockSource} />);
    
    const chip = screen.getByText('[1]');
    fireEvent.mouseEnter(chip);

    expect(screen.getByText(/BitDelta India Regulatory Review/i)).toBeInTheDocument();
    expect(screen.getByText(/example.com/i)).toBeInTheDocument();
  });
});

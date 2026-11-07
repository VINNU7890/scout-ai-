import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ComparisonTable } from '../components/ComparisonTable';
import { Finding } from '../types';

describe('ComparisonTable Component', () => {
  const mockData = {
    'FIU-IND Compliance': {
      'BitDelta': 'Registered with FIU-IND since 2024',
      'CoinDCX': 'FIU-IND registered entity with ISO 27001',
      'CoinSwitch': 'FIU-IND registered with 20M users'
    },
    'Maker/Taker Fees': {
      'BitDelta': '0.1% maker / 0.1% taker',
      'CoinDCX': '0.2% standard spot fee',
      'CoinSwitch': 'Zero trading fees on INR pairs'
    }
  };

  const mockFindings: Finding[] = [
    {
      entity: 'BitDelta',
      aspect: 'FIU-IND Compliance',
      claim: 'Registered with FIU-IND since 2024',
      evidence_quote: 'BitDelta has achieved FIU-IND compliance for Indian operations.',
      source_url: 'https://bitdelta.com/compliance',
      source_type: 'web',
      retrieved_at: new Date().toISOString(),
      confidence: 'high'
    }
  ];

  it('renders all entities and aspect rows', () => {
    render(<ComparisonTable comparisonData={mockData} findings={mockFindings} />);

    expect(screen.getByText('BitDelta')).toBeInTheDocument();
    expect(screen.getByText('CoinDCX')).toBeInTheDocument();
    expect(screen.getByText('CoinSwitch')).toBeInTheDocument();
    expect(screen.getByText('FIU-IND Compliance')).toBeInTheDocument();
    expect(screen.getByText('Maker/Taker Fees')).toBeInTheDocument();
  });

  it('opens evidence modal on cell click', () => {
    render(<ComparisonTable comparisonData={mockData} findings={mockFindings} />);

    const cell = screen.getByText('Registered with FIU-IND since 2024');
    fireEvent.click(cell);

    expect(screen.getByText(/Verified Quotes & Sources/i)).toBeInTheDocument();
    expect(screen.getByText(/BitDelta has achieved FIU-IND compliance/i)).toBeInTheDocument();
  });
});

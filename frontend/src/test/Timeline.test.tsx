import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Timeline } from '../components/Timeline';
import { RunEventPayload } from '../types';

describe('Timeline Component', () => {
  it('renders pipeline stages', () => {
    render(
      <Timeline
        status="completed"
        events={[]}
        sourcesCount={5}
        findingsCount={12}
      />
    );

    expect(screen.getByText(/Plan & Target Setup/i)).toBeInTheDocument();
    expect(screen.getByText(/Web Intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/Document Vector RAG/i)).toBeInTheDocument();
    expect(screen.getByText(/Strategic Synthesis/i)).toBeInTheDocument();
    expect(screen.getByText(/Drafting Executive Brief/i)).toBeInTheDocument();
    expect(screen.getByText(/Citation & Fact Verifier/i)).toBeInTheDocument();
  });

  it('displays active stage correctly when running', () => {
    const mockEvents: RunEventPayload[] = [
      {
        id: 1,
        run_id: 'test_123',
        event: 'node_started',
        stage: 'web_research',
        message: 'Searching DuckDuckGo for BitDelta competitors',
        timestamp: new Date().toISOString()
      }
    ];

    render(
      <Timeline
        status="researching"
        events={mockEvents}
        sourcesCount={3}
        findingsCount={6}
      />
    );

    expect(screen.getByText(/Searching DuckDuckGo/i)).toBeInTheDocument();
  });

  it('shows checkmarks for completed stages', () => {
    const mockEvents: RunEventPayload[] = [
      {
        id: 1,
        run_id: 'test_123',
        event: 'node_finished',
        stage: 'plan',
        message: 'Identified 4 competitors and 6 focus aspects',
        timestamp: new Date().toISOString()
      }
    ];

    render(
      <Timeline
        status="researching"
        events={mockEvents}
        sourcesCount={0}
        findingsCount={0}
      />
    );

    expect(screen.getByText(/Identified 4 competitors/i)).toBeInTheDocument();
  });
});

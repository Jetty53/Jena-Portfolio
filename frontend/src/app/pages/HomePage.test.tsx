import { screen } from '@testing-library/react';
import HomePage from './HomePage';
import { renderWithRouter } from '../../test-utils';

describe('HomePage', () => {
  it('shows recruiter proof and Jena', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText(/Jeet Nath — AI Developer/i)).toBeInTheDocument();
    expect(screen.getByText('RAG Portfolio Assistant')).toBeInTheDocument();
    expect(screen.getByText("Hey, I'm Jena.")).toBeInTheDocument();
  });
});

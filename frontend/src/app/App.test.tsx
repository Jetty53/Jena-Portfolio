import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

describe('App', () => {
  it('renders home dashboard', () => {
    render(<MemoryRouter><App /></MemoryRouter>);
    expect(screen.getByText(/Jeet Nath — AI Developer/i)).toBeInTheDocument();
    expect(screen.getByText(/Ask Jena if I'm a fit/i)).toBeInTheDocument();
  });
});

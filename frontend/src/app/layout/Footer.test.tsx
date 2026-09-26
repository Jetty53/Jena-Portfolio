import { screen } from '@testing-library/react';
import Footer from './Footer';
import { renderWithRouter } from '../../test-utils';

describe('Footer', () => {
  it('renders copyright', () => {
    renderWithRouter(<Footer />);
    expect(screen.getByText(/© 2026 Jeet Nath/i)).toBeInTheDocument();
  });
});

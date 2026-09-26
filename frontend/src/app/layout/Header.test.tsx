import { screen } from '@testing-library/react';
import Header from './Header';
import { renderWithRouter } from '../../test-utils';

describe('Header', () => {
  it('renders nav links', () => {
    renderWithRouter(<Header />);
    expect(screen.getByText('Jeet Nath')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'About' })).toBeInTheDocument();
    expect(screen.getByLabelText('GitHub')).toBeInTheDocument();
    expect(screen.getByLabelText('LinkedIn')).toBeInTheDocument();
  });
});

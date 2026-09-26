import { screen } from '@testing-library/react';
import Layout from './Layout';
import { renderWithRouter } from '../../test-utils';

describe('Layout', () => {
  it('wraps children with header and footer', () => {
    renderWithRouter(<Layout><p>Content</p></Layout>);
    expect(screen.getByText('Jeet Nath')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText(/© 2026/i)).toBeInTheDocument();
  });
});

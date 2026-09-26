import { render, screen } from '@testing-library/react';
import AboutPage from './AboutPage';

describe('AboutPage', () => {
  it('renders skills', () => {
    render(<AboutPage />);
    expect(screen.getByText('Python')).toBeInTheDocument();
  });
});

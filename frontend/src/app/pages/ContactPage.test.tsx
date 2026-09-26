import { render, screen } from '@testing-library/react';
import ContactPage from './ContactPage';

describe('ContactPage', () => {
  it('renders contact form', () => {
    render(<ContactPage />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send message' })).toBeInTheDocument();
  });
});

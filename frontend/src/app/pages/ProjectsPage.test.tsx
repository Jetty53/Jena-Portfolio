import { render, screen } from '@testing-library/react';
import ProjectsPage from './ProjectsPage';

describe('ProjectsPage', () => {
  it('renders project cards', () => {
    render(<ProjectsPage />);
    expect(screen.getByText('RAG Portfolio Assistant')).toBeInTheDocument();
  });
});

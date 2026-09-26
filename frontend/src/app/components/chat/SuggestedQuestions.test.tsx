import { render, screen, fireEvent } from '@testing-library/react';
import SuggestedQuestions from './SuggestedQuestions';

describe('SuggestedQuestions', () => {
  it('calls onSelect when chip clicked', () => {
    const onSelect = vi.fn();
    render(<SuggestedQuestions onSelect={onSelect} />);
    fireEvent.click(screen.getByText(/Is Jeet a match/i));
    expect(onSelect).toHaveBeenCalled();
  });
});

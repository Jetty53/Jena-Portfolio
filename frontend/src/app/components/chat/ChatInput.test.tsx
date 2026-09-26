import { render, screen, fireEvent } from '@testing-library/react';
import ChatInput from './ChatInput';

describe('ChatInput', () => {
  it('calls onSend on submit', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);
    fireEvent.change(screen.getByLabelText('Chat message'), { target: { value: 'Hello' } });
    fireEvent.click(screen.getByLabelText('Send message'));
    expect(onSend).toHaveBeenCalledWith('Hello');
  });
});

import { useState, type FormEvent, type KeyboardEvent } from 'react';
import { SendIcon } from '../Icons';

type Props = {
  value?: string;
  onChange?: (v: string) => void;
  onSend?: (v: string) => void;
  disabled?: boolean;
};

export default function ChatInput({ value: external, onChange, onSend, disabled }: Props) {
  const [internal, setInternal] = useState('');
  const value = onChange ? (external ?? '') : internal;
  const setValue = onChange ?? setInternal;

  const send = () => {
    if (!value.trim() || disabled) return;
    onSend?.(value.trim());
    setValue('');
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    send();
  };

  return (
    <div className="chat-input-area">
      <form className="input-wrapper" onSubmit={onSubmit}>
        <textarea
          className="chat-textarea"
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
          placeholder="Ask if Jeet matches your role..."
          aria-label="Chat message"
        />
        <div className="input-actions">
          <button type="submit" className="send-btn" aria-label="Send message" disabled={disabled}>
            <SendIcon />
          </button>
        </div>
      </form>
      <div className="input-hint">
        <span>Answers include source citations</span>
        <span>Press <kbd>Enter</kbd> to send</span>
      </div>
    </div>
  );
}

import { SUGGESTIONS } from '../../data/suggestions';

type Props = { onSelect?: (q: string) => void };

export default function SuggestedQuestions({ onSelect }: Props) {
  return (
    <div className="suggestions">
      <p className="suggestions-label">Suggested questions</p>
      <div className="suggestion-grid">
        {SUGGESTIONS.map((q) => (
          <button key={q} type="button" className="suggestion-chip" onClick={() => onSelect?.(q)}>
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

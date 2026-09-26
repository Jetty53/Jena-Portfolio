import { useRef, useState } from 'react';
import { askRetrieverStream } from '../../api/retriever';
import { SparkleIcon } from '../Icons';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';

type ChatMsg = { role: 'user' | 'assistant'; content: string; sources?: string[] };

export default function ChatShell() {
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionId = useRef(crypto.randomUUID());

  const patchLastAssistant = (fn: (msg: ChatMsg) => ChatMsg) => {
    setMessages((m) => {
      const copy = [...m];
      const i = copy.length - 1;
      if (i < 0 || copy[i].role !== 'assistant') return m;
      copy[i] = fn(copy[i]);
      return copy;
    });
  };

  const send = async (text: string) => {
    const question = text.trim();
    if (!question || pending) return;
    setError(null);
    setDraft('');
    const prior = messages.map(({ role, content }) => ({ role, content }));
    setMessages((m) => [...m, { role: 'user', content: question }, { role: 'assistant', content: '' }]);
    setPending(true);
    try {
      await askRetrieverStream(
        {
          question,
          session_id: sessionId.current,
          history: prior,
        },
        {
          onMeta: (data) => {
            if (data.session_id) sessionId.current = data.session_id;
            const sources = [...new Set((data.sources || []).map((s) => s.filename))];
            patchLastAssistant((msg) => ({ ...msg, sources }));
          },
          onToken: (t) => {
            patchLastAssistant((msg) => ({ ...msg, content: msg.content + t }));
          },
          onDone: (data) => {
            if (data.session_id) sessionId.current = data.session_id;
            const sources = [...new Set((data.sources || []).map((s) => s.filename))];
            patchLastAssistant((msg) => ({
              ...msg,
              content: data.answer || msg.content,
              sources: sources.length ? sources : msg.sources,
            }));
          },
          onError: (message) => setError(message),
        },
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'request failed';
      setError(msg);
      patchLastAssistant((m) => ({
        ...m,
        content: m.content || 'I could not reach the retrieval service.',
      }));
    } finally {
      setPending(false);
    }
  };

  const empty = messages.length === 0;

  return (
    <div className="chat-shell">
      <div className="chat-toolbar">
        <div className="chat-toolbar-left">
          <div className="chat-avatar">
            <SparkleIcon />
          </div>
          <div>
            <div className="chat-meta-title">Ask Jena if I'm a fit</div>
            <div className="chat-meta-sub">Jena · AI assistant</div>
          </div>
        </div>
        <div className="chat-toolbar-right">
          <span className="kb-pill">Custom RAG · citations</span>
        </div>
      </div>
      <div className={`chat-messages${empty ? ' chat-messages--empty' : ''}`}>
        {empty ? (
          <div className="chat-empty">
            <p className="chat-empty-title">Hey, I'm Jena.</p>
            <p className="chat-empty-text">
              Jeet’s RAG assistant. I answer from his CV, GitHub, and projects — with sources you can verify.
            </p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={`${msg.role}-${i}`} className={`message ${msg.role}`}>
              <div className="message-avatar">{msg.role === 'user' ? 'You' : 'J'}</div>
              <div className="message-body">
                <div className="message-label">{msg.role === 'user' ? 'You' : 'Jena'}</div>
                <div className="message-bubble">
                  {msg.content || (pending && msg.role === 'assistant' ? 'Retrieving…' : '')}
                </div>
                {msg.sources && msg.sources.length > 0 ? (
                  <div className="message-label">Sources: {msg.sources.join(' · ')}</div>
                ) : null}
              </div>
            </div>
          ))
        )}
        {error ? <p className="chat-empty-text">{error}</p> : null}
      </div>
      {empty ? <SuggestedQuestions onSelect={setDraft} /> : null}
      <ChatInput value={draft} onChange={setDraft} onSend={send} disabled={pending} />
    </div>
  );
}

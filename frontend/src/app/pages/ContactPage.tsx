import { type FormEvent } from 'react';

export default function ContactPage() {
  const onSubmit = (e: FormEvent<HTMLFormElement>) => e.preventDefault();

  return (
    <div className="page page--narrow">
      <header className="page-header">
        <h1 className="page-title">Contact</h1>
        <p className="page-lead">Open to AI/ML roles, collaborations, and interesting projects.</p>
      </header>
      <div className="contact-layout">
        <div className="contact-info">
          <a href="mailto:hello@jeetnath.dev" className="contact-link">
            <span className="contact-link-label">Email</span>
            <span className="contact-link-value">hello@jeetnath.dev</span>
          </a>
          <a href="#" className="contact-link">
            <span className="contact-link-label">GitHub</span>
            <span className="contact-link-value">github.com/jeetnath</span>
          </a>
        </div>
        <form className="contact-form" onSubmit={onSubmit}>
          <div className="form-field">
            <label htmlFor="name">Name</label>
            <input id="name" name="name" placeholder="Your name" />
          </div>
          <div className="form-field">
            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" placeholder="you@company.com" />
          </div>
          <div className="form-field">
            <label htmlFor="message">Message</label>
            <textarea id="message" name="message" rows={5} placeholder="Tell me about the role or project..." />
          </div>
          <button type="submit" className="btn-primary">Send message</button>
        </form>
      </div>
    </div>
  );
}

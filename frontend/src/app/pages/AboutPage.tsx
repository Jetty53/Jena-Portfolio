import { SKILLS } from '../data/skills';

export default function AboutPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">About</h1>
        <p className="page-lead">AI Developer building intelligent systems — from RAG pipelines to production-ready ML applications.</p>
      </header>
      <section className="page-section">
        <h2 className="section-label">Bio</h2>
        <p className="body-text">
          I'm Jeet Nath, an AI Developer focused on building practical AI systems — retrieval-augmented generation,
          LLM integrations, and end-to-end ML pipelines.
        </p>
      </section>
      <section className="page-section">
        <h2 className="section-label">Skills</h2>
        <div className="tag-grid">{SKILLS.map((s) => <span key={s} className="tag">{s}</span>)}</div>
      </section>
      <section className="page-section">
        <h2 className="section-label">Experience</h2>
        <div className="timeline">
          <div className="timeline-item">
            <span className="timeline-date">2024 — Present</span>
            <h3 className="timeline-title">AI Developer</h3>
            <p className="timeline-desc">Building RAG systems, custom ingestors, and AI-powered developer tools.</p>
          </div>
          <div className="timeline-item">
            <span className="timeline-date">2022 — 2024</span>
            <h3 className="timeline-title">Software Engineer</h3>
            <p className="timeline-desc">Full-stack development with growing focus on ML integration and data pipelines.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

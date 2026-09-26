import { Link } from 'react-router-dom';
import ChatShell from '../components/chat/ChatShell';
import { ArrowIcon } from '../components/Icons';
import { PROJECTS } from '../data/projects';
import { HIGHLIGHT_SKILLS } from '../data/skills';

const FEATURED = PROJECTS.slice(0, 2);

export default function HomePage() {
  return (
    <section className="dashboard">
      <div className="dashboard-left">
        <p className="hero-badge">
          <span className="status-dot" />
          Open to AI / ML roles
        </p>
        <h1 className="page-title">Jeet Nath — AI Developer</h1>
        <p className="dashboard-line">
          <span>Ask Jena if I'm a match for your role.</span>
        </p>
        <p className="page-lead">
          I build RAG systems — ingestion, retrieval, and sourced answers. Scan the highlights, or ask Jena for a fit check.
        </p>

        <section className="page-section">
          <h2 className="section-label">Stack</h2>
          <div className="tag-grid">
            {HIGHLIGHT_SKILLS.map((s) => (
              <span key={s} className="tag">{s}</span>
            ))}
          </div>
        </section>

        <section className="page-section">
          <h2 className="section-label">Featured work</h2>
          <div className="feature-list">
            {FEATURED.map((p) => (
              <article key={p.name} className="feature-card">
                <div className="project-card-top">
                  <h3 className="project-name">{p.name}</h3>
                  <span className="project-year">{p.year}</span>
                </div>
                <p className="project-desc">{p.desc}</p>
              </article>
            ))}
          </div>
          <Link to="/projects" className="text-link">
            All projects <ArrowIcon size={14} />
          </Link>
        </section>
      </div>

      <div className="dashboard-right">
        <ChatShell />
      </div>
    </section>
  );
}

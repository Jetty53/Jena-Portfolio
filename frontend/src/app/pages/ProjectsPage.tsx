import { PROJECTS } from '../data/projects';

export default function ProjectsPage() {
  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Projects</h1>
        <p className="page-lead">Selected work in AI, RAG, and full-stack development.</p>
      </header>
      <div className="project-grid">
        {PROJECTS.map((p) => (
          <article key={p.name} className="project-card">
            <div className="project-card-top">
              <h2 className="project-name">{p.name}</h2>
              <span className="project-year">{p.year}</span>
            </div>
            <p className="project-desc">{p.desc}</p>
            <div className="tag-grid tag-grid--sm">{p.tags.map((t) => <span key={t} className="tag">{t}</span>)}</div>
            <div className="project-links">{p.links.map((l) => <a key={l.label} href={l.href}>{l.label}</a>)}</div>
          </article>
        ))}
      </div>
    </div>
  );
}

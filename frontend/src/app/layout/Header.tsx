import { NavLink } from 'react-router-dom';
import { DownloadIcon, GitHubIcon, LinkedInIcon } from '../components/Icons';

const nav = [
  { to: '/', label: 'Home', end: true },
  { to: '/about', label: 'About' },
  { to: '/projects', label: 'Projects' },
  { to: '/contact', label: 'Contact' },
];

export default function Header() {
  return (
    <header className="site-header">
      <div className="header-inner">
        <NavLink to="/" className="brand">
          <div className="brand-text">
            <span className="brand-name">Jeet Nath</span>
            <span className="brand-role">AI Developer</span>
          </div>
        </NavLink>
        <nav className="header-nav" aria-label="Primary">
          {nav.map(({ to, label, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="header-actions">
          <a href="#" className="icon-btn" aria-label="GitHub">
            <GitHubIcon />
          </a>
          <a href="#" className="icon-btn" aria-label="LinkedIn">
            <LinkedInIcon />
          </a>
          <a href="#" className="btn-resume">
            <DownloadIcon />
            <span>Resume</span>
          </a>
        </div>
      </div>
    </header>
  );
}

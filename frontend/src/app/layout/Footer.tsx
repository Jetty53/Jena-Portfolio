import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-links">
        <a href="#">GitHub</a>
        <a href="#">LinkedIn</a>
        <Link to="/contact">Email</Link>
      </div>
      <span className="footer-copy">© 2026 Jeet Nath · AI Developer</span>
    </footer>
  );
}

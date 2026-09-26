import type { RouteObject } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import ProjectsPage from './pages/ProjectsPage';
import ContactPage from './pages/ContactPage';

export const routes: RouteObject[] = [
  { path: '/', element: <HomePage /> },
  { path: '/about', element: <AboutPage /> },
  { path: '/projects', element: <ProjectsPage /> },
  { path: '/contact', element: <ContactPage /> },
];

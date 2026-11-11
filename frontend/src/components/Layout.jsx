import { NavLink } from 'react-router-dom'
import { LogoutButton } from '../App.jsx'

const NAV = {
  student: [
    ['/student', 'Search'],
    ['/student/bookmarks', 'My Bookmarks'],
  ],
  scholar: [
    ['/scholar', 'Word Meanings'],
  ],
  editor: [
    ['/editor', 'Translations'],
    ['/editor/new', 'Add Mantra'],
    ['/editor/edit', 'Edit Mantra'],
    ['/editor/lock', 'Lock Demo'],
  ],
  admin: [
    ['/admin', 'Approve'],
    ['/admin/reports', 'Reports'],
    ['/admin/manage', 'Manage Data'],
    ['/admin/history', 'History'],
  ],
}

/** Top bar with the Om logo, role-based nav and the logged-in user. */
export default function Layout({ children }) {
  const auth = JSON.parse(localStorage.getItem('vedas_auth') || 'null')
  const links = auth ? NAV[auth.role] || [] : []
  return (
    <>
      <header className="topbar">
        <span className="logo">ॐ</span>
        <div className="brand">
          Vedas DBMS
          <small>VEDIC RESEARCH LIBRARY</small>
        </div>
        <nav className="nav">
          {links.map(([to, label]) => (
            <NavLink key={to} to={to}
              className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>
        {auth && (
          <span className="whoami">
            {auth.username} · {auth.role} <LogoutButton />
          </span>
        )}
      </header>
      <main className="page">
        <div className="divider"><span>❖ ❖ ❖</span></div>
        {children}
      </main>
    </>
  )
}

import { Navigate, NavLink, Route, Routes } from 'react-router-dom'
import { clearAuth, getAuth } from './api.js'
import Layout from './components/Layout.jsx'

import LoginPage from './pages/LoginPage.jsx'
import StudentSearchPage from './pages/StudentSearchPage.jsx'
import MyBookmarksPage from './pages/MyBookmarksPage.jsx'
import ScholarWordsPage from './pages/ScholarWordsPage.jsx'
import EditorTranslationsPage from './pages/EditorTranslationsPage.jsx'
import EditorNewMantraPage from './pages/EditorNewMantraPage.jsx'
import EditorMantraEditPage from './pages/EditorMantraEditPage.jsx'
import LockDemoPage from './pages/LockDemoPage.jsx'
import AdminApprovePage from './pages/AdminApprovePage.jsx'
import AdminReportsPage from './pages/AdminReportsPage.jsx'
import AdminManagePage from './pages/AdminManagePage.jsx'
import AdminHistoryPage from './pages/AdminHistoryPage.jsx'

/** Route guard: only the allowed role(s) get through; everyone else is
 * sent to /login. The backend re-checks the role on every call, so this
 * is convenience, not security. */
function RequireRole({ roles, children }) {
  const auth = getAuth()
  if (!auth) return <Navigate to="/login" replace />
  if (!roles.includes(auth.role)) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

function LogoutButton() {
  return (
    <button
      className="secondary small"
      onClick={() => {
        clearAuth()
        window.location.href = '/login'
      }}
    >
      Logout
    </button>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* student */}
      <Route path="/student" element={
        <RequireRole roles={['student']}><StudentSearchPage /></RequireRole>} />
      <Route path="/student/bookmarks" element={
        <RequireRole roles={['student']}><MyBookmarksPage /></RequireRole>} />

      {/* scholar */}
      <Route path="/scholar" element={
        <RequireRole roles={['scholar']}><ScholarWordsPage /></RequireRole>} />

      {/* editor */}
      <Route path="/editor" element={
        <RequireRole roles={['editor']}><EditorTranslationsPage /></RequireRole>} />
      <Route path="/editor/new" element={
        <RequireRole roles={['editor']}><EditorNewMantraPage /></RequireRole>} />
      <Route path="/editor/edit" element={
        <RequireRole roles={['editor']}><EditorMantraEditPage /></RequireRole>} />
      <Route path="/editor/lock" element={
        <RequireRole roles={['editor']}><LockDemoPage /></RequireRole>} />

      {/* admin */}
      <Route path="/admin" element={
        <RequireRole roles={['admin']}><AdminApprovePage /></RequireRole>} />
      <Route path="/admin/reports" element={
        <RequireRole roles={['admin']}><AdminReportsPage /></RequireRole>} />
      <Route path="/admin/manage" element={
        <RequireRole roles={['admin']}><AdminManagePage /></RequireRole>} />
      <Route path="/admin/history" element={
        <RequireRole roles={['admin']}><AdminHistoryPage /></RequireRole>} />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export { LogoutButton }

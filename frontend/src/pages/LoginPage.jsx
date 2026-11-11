import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, saveAuth } from '../api.js'
import { ErrorBanner } from '../components/Banners.jsx'

const ROLES = ['admin', 'editor', 'scholar', 'student']

/** Centered login card: Om, Sanskrit shloka, role + password. */
export default function LoginPage() {
  const [role, setRole] = useState('student')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const nav = useNavigate()

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const info = await api('/auth/login', {
        method: 'POST',
        body: { role, password },
      })
      saveAuth(info)
      nav(`/${role}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="om">ॐ</div>
        <div className="shloka">सत्यमेव जयते</div>
        <p className="muted" style={{ marginTop: 0 }}>
          "Truth alone triumphs" - Mundaka Upanishad
        </p>
        <div className="divider"><span>❖</span></div>
        <form onSubmit={submit}>
          <div className="field">
            <label htmlFor="role">Login as</label>
            <select id="role" value={role}
              onChange={(e) => setRole(e.target.value)}>
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="pw">MySQL password</label>
            <input id="pw" type="password" value={password}
              placeholder="password for {role}_u"
              onChange={(e) => setPassword(e.target.value)} />
          </div>
          <ErrorBanner>{error}</ErrorBanner>
          <button type="submit" disabled={busy}>
            {busy ? 'Connecting…' : 'Enter'}
          </button>
        </form>
        <p className="muted" style={{ marginTop: '0.9rem', fontSize: '0.8rem' }}>
          The API connects to MySQL <b>as this role&apos;s own user</b>, so the
          database itself enforces every permission.
        </p>
      </div>
    </div>
  )
}

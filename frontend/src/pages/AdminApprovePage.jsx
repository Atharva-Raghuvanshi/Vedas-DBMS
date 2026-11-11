import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner, OkBanner } from '../components/Banners.jsx'

/** Admin: approve pending translations (only admin may UPDATE status). */
export default function AdminApprovePage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  async function load() {
    try {
      const data = await api('/admin/translations?status=pending')
      setRows(data.rows)
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { load() }, [])

  async function approve(tid) {
    setMsg(''); setError('')
    try {
      const r = await api(`/admin/translations/${tid}/approve`,
        { method: 'POST' })
      setMsg(r.message)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Pending Translations</h1>
      <p className="muted">
        Approving sets <code>status=&apos;approved&apos;</code> - after that
        the translation becomes visible to students. An editor attempting
        this gets MySQL error 1143 (column-level grant).
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>
      {rows.length === 0 && <p>Nothing pending. 🎉</p>}
      {rows.map((t) => (
        <div className="mantra-card" key={t.translation_id}>
          <div className="tags" style={{ marginBottom: '0.4rem' }}>
            <span className="tag status-pending">pending</span>
            <span className="tag">translation #{t.translation_id}</span>
            <span className="tag">mantra #{t.mantra_id}</span>
            <span className="tag rishi">{t.translator_name}</span>
          </div>
          <p className="translation">{t.text}</p>
          <button onClick={() => approve(t.translation_id)}>
            ✔ Approve
          </button>
        </div>
      ))}
    </>
  )
}

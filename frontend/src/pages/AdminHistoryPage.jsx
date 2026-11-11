import { useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner } from '../components/Banners.jsx'

/** Admin: view Mantra_History - who changed which Mantra and what the
 * old text was (written by the editor's transactional edit). */
export default function AdminHistoryPage() {
  const [mantraId, setMantraId] = useState('')
  const [rows, setRows] = useState(null)
  const [error, setError] = useState('')

  async function load() {
    setError('')
    try {
      const qs = mantraId ? `?mantra_id=${mantraId}` : ''
      const data = await api('/admin/history' + qs)
      setRows(data.rows)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Mantra Edit History</h1>
      <p className="muted">
        Every transactional edit archives the old text here before the
        UPDATE commits.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <div className="toolbar">
        <div className="field" style={{ maxWidth: 200 }}>
          <label>Mantra ID (empty = all)</label>
          <input type="number" min="1" value={mantraId}
            onChange={(e) => setMantraId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()} />
        </div>
        <button onClick={load}>Load history</button>
      </div>

      {rows && (
        <table className="data">
          <thead>
            <tr><th>#</th><th>Mantra</th><th>Old Sanskrit</th>
              <th>Old IAST</th><th>Changed by</th><th>At</th></tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan="6" className="muted">No history rows.</td>
              </tr>)}
            {rows.map((h) => (
              <tr key={h.history_id}>
                <td>{h.history_id}</td>
                <td>#{h.mantra_id}</td>
                <td style={{ fontFamily: "'Tiro Devanagari Sanskrit', serif",
                  fontSize: '1.05rem', maxWidth: 320 }}>
                  {h.old_sanskrit_text || '—'}</td>
                <td style={{ fontStyle: 'italic', maxWidth: 280 }}>
                  {h.old_iast_text || '—'}</td>
                <td>{h.changed_by}</td>
                <td>{String(h.changed_at).replace('T', ' ').slice(0, 19)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  )
}

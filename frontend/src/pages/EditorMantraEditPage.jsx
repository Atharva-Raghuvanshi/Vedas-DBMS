import { useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner, InfoBanner, OkBanner } from '../components/Banners.jsx'

/** Editor: edit a Mantra inside a real transaction:
 * START TRANSACTION -> SELECT ... FOR UPDATE -> insert old text into
 * Mantra_History -> UPDATE -> COMMIT (ROLLBACK on any error).
 * The API returns the old text it archived, shown here for the viva. */
export default function EditorMantraEditPage() {
  const [mantraId, setMantraId] = useState('')
  const [sanskrit, setSanskrit] = useState('')
  const [iast, setIast] = useState('')
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [archived, setArchived] = useState(null)

  async function submit(e) {
    e.preventDefault()
    setMsg(''); setError(''); setArchived(null)
    try {
      const r = await api(`/editor/mantras/${mantraId}/edit`,
        { method: 'POST',
          body: { sanskrit_text: sanskrit, iast_text: iast } })
      setMsg(r.message)
      setArchived(r)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Edit a Mantra (transaction)</h1>
      <p className="muted">
        The backend runs: <code>START TRANSACTION → SELECT … FOR UPDATE →
        INSERT Mantra_History → UPDATE → COMMIT</code>, rolling back on any
        error. The old text is archived in <code>Mantra_History</code>.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>
      <form onSubmit={submit} className="card">
        <div className="field" style={{ maxWidth: 200 }}>
          <label>Mantra ID</label>
          <input type="number" min="1" required value={mantraId}
            onChange={(e) => setMantraId(e.target.value)} />
        </div>
        <div className="field">
          <label>New Sanskrit text</label>
          <textarea required value={sanskrit}
            onChange={(e) => setSanskrit(e.target.value)} />
        </div>
        <div className="field">
          <label>New IAST text</label>
          <textarea value={iast}
            onChange={(e) => setIast(e.target.value)} />
        </div>
        <button type="submit">Save edit (transaction)</button>
      </form>

      {archived && (
        <div className="card">
          <h3>Archived to Mantra_History</h3>
          {archived.old_sanskrit_text && (
            <div className="sanskrit" style={{ fontSize: '1.1rem' }}>
              {archived.old_sanskrit_text}</div>
          )}
          {archived.old_iast_text && (
            <div className="iast">{archived.old_iast_text}</div>
          )}
          <InfoBanner>changed_by: {archived.changed_by}</InfoBanner>
        </div>
      )}
    </>
  )
}

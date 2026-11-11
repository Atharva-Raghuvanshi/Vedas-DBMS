import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner, InfoBanner, OkBanner } from '../components/Banners.jsx'

/** Lock demo (PRD section 6): open this page in TWO browser tabs.
 * Tab 1 locks the row and holds it; tab 2 then waits until tab 1 commits. */
export default function LockDemoPage() {
  const [mantraId, setMantraId] = useState('1')
  const [holding, setHolding] = useState(null)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  useEffect(() => {
    api('/editor/lock/status')
      .then((r) => setHolding(r.mantra_id))
      .catch(() => {})
  }, [])

  async function start() {
    setMsg(''); setError('')
    try {
      const r = await api('/editor/lock/start', { method: 'POST',
        body: { mantra_id: Number(mantraId) } })
      setMsg(r.message)
      setHolding(r.mantra_id)
    } catch (err) {
      setError(err.message)
    }
  }

  async function commit() {
    setMsg(''); setError('')
    try {
      const r = await api('/editor/lock/commit', { method: 'POST' })
      setMsg(r.message)
      setHolding(null)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Row-Lock Demo</h1>
      <InfoBanner>
        Open this page in two browser tabs (both logged in as editor).
        Tab 1: <b>Lock row</b> - tab 2: <b>Lock row</b> on the same Mantra
        will hang until tab 1 commits. The backend holds the open
        transaction with <code>SELECT … FOR UPDATE</code>.
      </InfoBanner>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>
      <div className="card">
        <div className="toolbar">
          <div className="field" style={{ maxWidth: 200 }}>
            <label>Mantra ID</label>
            <input type="number" min="1" value={mantraId}
              onChange={(e) => setMantraId(e.target.value)} />
          </div>
          <button onClick={start} disabled={holding != null}>
            🔒 Lock row (start transaction)
          </button>
          <button className="secondary" onClick={commit}
            disabled={holding == null}>
            ✔ Commit (release lock)
          </button>
        </div>
        <p className="muted">
          {holding != null
            ? `You are holding the lock on mantra ${holding}. Other editors wait...`
            : 'You hold no lock.'}
        </p>
      </div>
      <p className="muted">
        CLI backup: <code>sql/06_concurrency_demo.sql</code> · headless
        proof: <code>scripts/test_locking.py</code>
      </p>
    </>
  )
}

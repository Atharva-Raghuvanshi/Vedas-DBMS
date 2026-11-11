import { useEffect, useState } from 'react'
import { api } from '../api.js'
import MantraCard from '../components/MantraCard.jsx'
import Pagination from '../components/Pagination.jsx'
import { ErrorBanner, InfoBanner, OkBanner } from '../components/Banners.jsx'

const EMPTY = { veda: '', kanda: '', sukta: '', rishi: '', deity: '',
  metre: '', theme: '', word: '' }

/** Student search: dropdown + text filters, paginated mantra cards,
 * bookmark buttons, and the permission-denied demo (F11). */
export default function StudentSearchPage() {
  const [filters, setFilters] = useState(EMPTY)
  const [opts, setOpts] = useState({})
  const [result, setResult] = useState(null)
  const [page, setPage] = useState(1)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [denied, setDenied] = useState(null)
  const [mine, setMine] = useState(new Set())
  const [busy, setBusy] = useState(false)

  async function loadOptions() {
    try {
      const kinds = ['veda', 'kanda', 'sukta', 'rishi', 'deity', 'theme',
        'metre']
      const all = await Promise.all(kinds.map(async (k) =>
        [k, await api(`/options/${kind_safely(k)}`)]))
      setOpts(Object.fromEntries(all))
    } catch (err) {
      setError(err.message)
    }
  }
  function kind_safely(k) { return k }   // kept simple on purpose

  async function load(p = 1) {
    setBusy(true)
    setError('')
    try {
      const qs = new URLSearchParams({ page: String(p), size: '20' })
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== '') qs.set(k, v)
      })
      const data = await api('/student/mantras?' + qs.toString())
      setResult(data)
      setPage(p)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function loadMine() {
    try {
      const data = await api('/student/bookmarks')
      setMine(new Set(data.rows.map((r) => r.mantra_id)))
    } catch { /* non-fatal */ }
  }

  useEffect(() => { loadOptions(); loadMine() }, [])

  async function bookmark(m) {
    setMsg(''); setError('')
    try {
      if (mine.has(m.mantra_id)) {
        await api(`/student/bookmarks/${m.mantra_id}`, { method: 'DELETE' })
        setMsg(`Removed bookmark on mantra ${m.mantra_id}.`)
      } else {
        await api('/student/bookmarks', { method: 'POST',
          body: { mantra_id: m.mantra_id } })
        setMsg(`Bookmarked mantra ${m.mantra_id}.`)
      }
      await loadMine()
    } catch (err) {
      setError(err.message)
    }
  }

  async function demoDenied() {
    setDenied(null); setError('')
    try {
      setDenied(await api('/student/demo-denied'))
    } catch (err) {
      setError(err.message)
    }
  }

  function set(k, v) {
    setFilters((f) => ({ ...f, [k]: v }))
  }

  return (
    <>
      <h1>Search the Mantras</h1>
      <p className="muted">
        Read-only browse through <code>v_student_mantras</code> - approved
        translations only.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>

      <div className="card">
        <div className="toolbar">
          <div className="field">
            <label>Veda</label>
            <select value={filters.veda}
              onChange={(e) => set('veda', e.target.value)}>
              <option value="">any</option>
              {(opts.veda || []).map((o) => (
                <option key={o.label} value={o.label}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Kanda</label>
            <select value={filters.kanda}
              onChange={(e) => set('kanda', e.target.value)}>
              <option value="">any</option>
              {(opts.kanda || []).map((o) => (
                <option key={o.item_id ?? o.label} value={o.label}>
                  {o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Sukta</label>
            <select value={filters.sukta}
              onChange={(e) => set('sukta', e.target.value)}>
              <option value="">any</option>
              {(opts.sukta || []).map((o) => (
                <option key={o.item_id ?? o.label} value={o.sukta_number ??
                  o.label.split('.').pop()}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Rishi</label>
            <select value={filters.rishi}
              onChange={(e) => set('rishi', e.target.value)}>
              <option value="">any</option>
              {(opts.rishi || []).map((o) => (
                <option key={o.label} value={o.label}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Deity</label>
            <select value={filters.deity}
              onChange={(e) => set('deity', e.target.value)}>
              <option value="">any</option>
              {(opts.deity || []).map((o) => (
                <option key={o.label} value={o.label}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Metre</label>
            <select value={filters.metre}
              onChange={(e) => set('metre', e.target.value)}>
              <option value="">any</option>
              {(opts.metre || []).map((o) => (
                <option key={o.label} value={o.label}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Theme</label>
            <select value={filters.theme}
              onChange={(e) => set('theme', e.target.value)}>
              <option value="">any</option>
              {(opts.theme || []).map((o) => (
                <option key={o.label} value={o.label}>{o.label}</option>))}
            </select>
          </div>
          <div className="field" style={{ minWidth: 220 }}>
            <label>Sanskrit word (contains)</label>
            <input value={filters.word} placeholder="e.g. अग्नि"
              onChange={(e) => set('word', e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && load(1)} />
          </div>
          <button onClick={() => load(1)} disabled={busy}>
            {busy ? '…' : 'Search'}
          </button>
        </div>
      </div>

      {result && (
        <>
          <InfoBanner>
            {result.total} mantras match · showing page {result.page} of{' '}
            {result.pages}
          </InfoBanner>
          {result.rows.length === 0 && <p>No mantras match these filters.</p>}
          {result.rows.map((m) => (
            <MantraCard key={m.mantra_id} m={m}
              actions={
                <button className={mine.has(m.mantra_id) ? 'secondary'
                  : ''} onClick={() => bookmark(m)}>
                  {mine.has(m.mantra_id) ? '★ Remove bookmark'
                    : '☆ Bookmark'}
                </button>
              } />
          ))}
          <Pagination page={page} pages={result.pages}
            onPage={(p) => load(p)} />
        </>
      )}

      <div className="divider"><span>❖ ❖ ❖</span></div>
      <h2>Permission demo (F11)</h2>
      <p className="muted">
        A student has no UPDATE grant on <code>Mantras</code>. MySQL blocks
        the write; the API surfaces the raw error.
      </p>
      <button className="secondary" onClick={demoDenied}>
        Try to edit a Mantra (should fail)
      </button>
      {denied && (
        <InfoBanner>
          {denied.denied
            ? `Blocked by MySQL: ${denied.message}`
            : denied.message}
        </InfoBanner>
      )}
    </>
  )
}

import { useEffect, useState } from 'react'
import { api } from '../api.js'
import Pagination from '../components/Pagination.jsx'
import { ErrorBanner, OkBanner } from '../components/Banners.jsx'

/** Editor: add a translation (saved as pending) over a searchable,
 * paginated list from v_editor_mantras. */
export default function EditorTranslationsPage() {
  const [rows, setRows] = useState(null)
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({ mantra_id: '', translator_name: '',
    text: '' })

  async function load(p = 1) {
    setError('')
    try {
      const data = await api(`/editor/mantras?page=${p}&size=10` +
        (search ? `&search=${encodeURIComponent(search)}` : ''))
      setRows(data.rows); setTotal(data.total)
      setPages(data.pages); setPage(p)
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { load(1) }, [])

  async function addTranslation(e) {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const r = await api('/editor/translations', { method: 'POST',
        body: { mantra_id: Number(form.mantra_id),
          translator_name: form.translator_name, text: form.text } })
      setMsg(r.message)
      setForm({ mantra_id: '', translator_name: '', text: '' })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Add a Translation</h1>
      <p className="muted">
        New translations are saved with status <b>pending</b> - only an
        admin can approve them.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>

      <form onSubmit={addTranslation} className="card">
        <div className="form-row">
          <div className="field" style={{ maxWidth: 160 }}>
            <label>Mantra ID</label>
            <input type="number" min="1" required value={form.mantra_id}
              onChange={(e) => setForm({ ...form,
                mantra_id: e.target.value })} />
          </div>
          <div className="field">
            <label>Translator name</label>
            <input required value={form.translator_name}
              onChange={(e) => setForm({ ...form,
                translator_name: e.target.value })} />
          </div>
        </div>
        <div className="field">
          <label>Translation</label>
          <textarea required value={form.text}
            onChange={(e) => setForm({ ...form, text: e.target.value })} />
        </div>
        <button type="submit">Submit (pending)</button>
      </form>

      <div className="divider"><span>❖ ❖ ❖</span></div>
      <h2>Browse Mantras</h2>
      <div className="toolbar">
        <div className="field" style={{ maxWidth: 320 }}>
          <label>Search text</label>
          <input value={search} placeholder="rishi, deity, metre, text…"
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load(1)} />
        </div>
        <button onClick={() => load(1)}>Search</button>
        <span className="muted">{total} mantras</span>
      </div>

      {rows && (
        <table className="data">
          <thead>
            <tr><th>ID</th><th>Location</th><th>Rishi</th><th>Deity</th>
              <th>Sanskrit</th><th>Pending</th><th>Approved</th></tr>
          </thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.mantra_id}>
                <td>{m.mantra_id}</td>
                <td>{m.veda_name} {m.sukta_number}.{m.mantra_number}</td>
                <td>{m.rishi_name}</td>
                <td>{m.deity_name}</td>
                <td style={{ maxWidth: 260 }}>
                  {m.sanskrit_text
                    ? <span style={{ fontFamily:
                        "'Tiro Devanagari Sanskrit', serif" }}>
                        {m.sanskrit_text.slice(0, 60)}…
                      </span>
                    : <span className="muted">—</span>}
                </td>
                <td>{m.pending_translations}</td>
                <td>{m.approved_translations}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <Pagination page={page} pages={pages} onPage={load} />
    </>
  )
}

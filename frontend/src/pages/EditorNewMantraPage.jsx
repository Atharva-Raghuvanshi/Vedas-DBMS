import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner, OkBanner } from '../components/Banners.jsx'

/** Editor: add a Mantra - Sukta / Rishi / Deity come from dropdowns
 * (options endpoint), never typed names. */
export default function EditorNewMantraPage() {
  const [opts, setOpts] = useState({})
  const [form, setForm] = useState({ sukta_id: '', rishi_id: '',
    deity_id: '', mantra_number: '', metre: '', sanskrit_text: '',
    iast_text: '' })
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  useEffect(() => {
    Promise.all(['sukta', 'rishi', 'deity', 'metre'].map(async (k) =>
      [k, await api(`/options/${k}`)]))
      .then((all) => setOpts(Object.fromEntries(all)))
      .catch((err) => setError(err.message))
  }, [])

  function set(k, v) { setForm((f) => ({ ...f, [k]: v })) }

  async function submit(e) {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const r = await api('/editor/mantras', { method: 'POST', body: {
        sukta_id: Number(form.sukta_id), rishi_id: Number(form.rishi_id),
        deity_id: Number(form.deity_id),
        mantra_number: Number(form.mantra_number),
        metre: form.metre, sanskrit_text: form.sanskrit_text,
        iast_text: form.iast_text } })
      setMsg(`${r.message} (mantra_id ${r.mantra_id})`)
      setForm({ sukta_id: '', rishi_id: '', deity_id: '', mantra_number: '',
        metre: '', sanskrit_text: '', iast_text: '' })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Add a Mantra</h1>
      <p className="muted">
        Link the new Mantra to its Sukta, Rishi and Deity by picking from
        the dropdowns. A duplicate (Sukta, mantra number) pair is rejected
        by a UNIQUE constraint.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>
      <form onSubmit={submit} className="card">
        <div className="form-row">
          <div className="field">
            <label>Sukta</label>
            <select required value={form.sukta_id}
              onChange={(e) => set('sukta_id', e.target.value)}>
              <option value="">choose…</option>
              {(opts.sukta || []).map((o) => (
                <option key={o.item_id} value={o.item_id}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Rishi</label>
            <select required value={form.rishi_id}
              onChange={(e) => set('rishi_id', e.target.value)}>
              <option value="">choose…</option>
              {(opts.rishi || []).map((o) => (
                <option key={o.item_id} value={o.item_id}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Deity</label>
            <select required value={form.deity_id}
              onChange={(e) => set('deity_id', e.target.value)}>
              <option value="">choose…</option>
              {(opts.deity || []).map((o) => (
                <option key={o.item_id} value={o.item_id}>{o.label}</option>))}
            </select>
          </div>
          <div className="field">
            <label>Mantra number</label>
            <input type="number" min="1" required value={form.mantra_number}
              onChange={(e) => set('mantra_number', e.target.value)} />
          </div>
          <div className="field">
            <label>Metre</label>
            <select value={form.metre}
              onChange={(e) => set('metre', e.target.value)}>
              <option value="">unknown</option>
              {(opts.metre || []).map((o) => (
                <option key={o.label} value={o.label}>{o.label}</option>))}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Sanskrit text</label>
          <textarea value={form.sanskrit_text}
            onChange={(e) => set('sanskrit_text', e.target.value)} />
        </div>
        <div className="field">
          <label>IAST text</label>
          <textarea value={form.iast_text}
            onChange={(e) => set('iast_text', e.target.value)} />
        </div>
        <button type="submit">Add Mantra</button>
      </form>
    </>
  )
}

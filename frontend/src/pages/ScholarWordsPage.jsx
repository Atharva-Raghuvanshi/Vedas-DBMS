import { useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner, OkBanner } from '../components/Banners.jsx'

/** Scholar: view word meanings of a Mantra (in order) and add new ones,
 * through v_scholar_words. */
export default function ScholarWordsPage() {
  const [mantraId, setMantraId] = useState('')
  const [rows, setRows] = useState(null)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [form, setForm] = useState({ word_order: '', sanskrit_word: '',
    dhatu: '', english_meaning: '' })
  const [edit, setEdit] = useState(null)   // {word_order, ...} being edited

  async function load(id = mantraId) {
    if (!id) return
    setError(''); setMsg('')
    try {
      const data = await api(`/scholar/words?mantra_id=${id}`)
      setRows(data.rows)
    } catch (err) {
      setError(err.message)
    }
  }

  async function addWord(e) {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const r = await api('/scholar/words', { method: 'POST',
        body: { mantra_id: Number(mantraId), word_order: Number(form.word_order),
          sanskrit_word: form.sanskrit_word, dhatu: form.dhatu,
          english_meaning: form.english_meaning } })
      setMsg(r.message)
      setForm({ word_order: '', sanskrit_word: '', dhatu: '',
        english_meaning: '' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function saveEdit() {
    setMsg(''); setError('')
    try {
      const r = await api('/scholar/words', { method: 'PUT', body: {
        mantra_id: Number(mantraId), word_order: edit.word_order,
        sanskrit_word: edit.sanskrit_word, dhatu: edit.dhatu,
        english_meaning: edit.english_meaning } })
      setMsg(r.message)
      setEdit(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Word Meanings (Scholar)</h1>
      <p className="muted">
        Padapāṭha-style breakdown, read through{' '}
        <code>v_scholar_words</code>.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>

      <div className="toolbar">
        <div className="field" style={{ maxWidth: 200 }}>
          <label>Mantra ID</label>
          <input type="number" min="1" value={mantraId}
            onChange={(e) => setMantraId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()} />
        </div>
        <button onClick={() => load()}>Load words</button>
      </div>

      {rows && (
        <table className="data">
          <thead>
            <tr>
              <th>#</th><th>Word</th><th>Dhātu (root)</th>
              <th>Meaning</th><th></th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan="5" className="muted">No words recorded for
                this Mantra yet.</td></tr>)}
            {rows.map((w) => (
              <tr key={w.word_order}>
                <td>{w.word_order}</td>
                {edit && edit.word_order === w.word_order ? (
                  <>
                    <td><input value={edit.sanskrit_word || ''}
                      onChange={(e) => setEdit({ ...edit,
                        sanskrit_word: e.target.value })} /></td>
                    <td><input value={edit.dhatu || ''}
                      onChange={(e) => setEdit({ ...edit,
                        dhatu: e.target.value })} /></td>
                    <td><input value={edit.english_meaning || ''}
                      onChange={(e) => setEdit({ ...edit,
                        english_meaning: e.target.value })} /></td>
                    <td>
                      <button className="small" onClick={saveEdit}>Save</button>{' '}
                      <button className="secondary small"
                        onClick={() => setEdit(null)}>Cancel</button>
                    </td>
                  </>
                ) : (
                  <>
                    <td style={{ fontFamily: "'Tiro Devanagari Sanskrit', serif",
                      fontSize: '1.1rem' }}>
                      {w.sanskrit_word || <span className="muted">—</span>}
                    </td>
                    <td>{w.dhatu || <span className="muted">—</span>}</td>
                    <td>{w.english_meaning}</td>
                    <td>
                      <button className="secondary small"
                        onClick={() => setEdit({ ...w })}>Edit</button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="divider"><span>❖ ❖ ❖</span></div>
      <h2>Add a word</h2>
      <form onSubmit={addWord} className="card">
        <div className="form-row">
          <div className="field">
            <label>Word order</label>
            <input type="number" min="1" required value={form.word_order}
              onChange={(e) => setForm({ ...form,
                word_order: e.target.value })} />
          </div>
          <div className="field">
            <label>Sanskrit word</label>
            <input required value={form.sanskrit_word}
              onChange={(e) => setForm({ ...form,
                sanskrit_word: e.target.value })} />
          </div>
          <div className="field">
            <label>Dhātu (root)</label>
            <input value={form.dhatu} placeholder="optional"
              onChange={(e) => setForm({ ...form, dhatu: e.target.value })} />
          </div>
          <div className="field">
            <label>English meaning</label>
            <input value={form.english_meaning}
              onChange={(e) => setForm({ ...form,
                english_meaning: e.target.value })} />
          </div>
        </div>
        <button type="submit">Add word</button>
      </form>
    </>
  )
}

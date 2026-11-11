import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { ErrorBanner, OkBanner } from '../components/Banners.jsx'

const ENTITIES = [
  ['vedas', 'Vedas', ['veda_name']],
  ['kandas', 'Kandas', ['veda_id', 'kanda_number']],
  ['suktas', 'Suktas', ['kanda_id', 'sukta_number']],
  ['rishis', 'Rishis', ['rishi_name']],
  ['deities', 'Deities', ['deity_name']],
  ['themes', 'Themes', ['theme_name']],
]

/** Admin manage-data page: add / edit / delete rows in the six reference
 * tables, and tag themes onto Mantras (Mantra_Themes). */
export default function AdminManagePage() {
  const [entity, setEntity] = useState('vedas')
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [editing, setEditing] = useState(null)   // row being edited
  const [form, setForm] = useState({})

  // theme tagging
  const [tagMantra, setTagMantra] = useState('')
  const [tagTheme, setTagTheme] = useState('')
  const [tags, setTags] = useState(null)

  const fields = ENTITIES.find(([k]) => k === entity)[2]

  async function load(k = entity) {
    setError('')
    try {
      const data = await api(`/admin/${k}`)
      setRows(data.rows)
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { setEditing(null); load(entity) }, [entity])

  async function add(e) {
    e.preventDefault()
    setMsg(''); setError('')
    try {
      const r = await api(`/admin/${entity}`, { method: 'POST', body: form })
      setMsg(r.message)
      setForm({})
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function saveEdit() {
    setMsg(''); setError('')
    try {
      const r = await api(`/admin/${entity}/${editing[pk()]}`,
        { method: 'PUT', body: editing })
      setMsg(r.message)
      setEditing(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function del(row) {
    setMsg(''); setError('')
    try {
      const r = await api(`/admin/${entity}/${row[pk()]}`,
        { method: 'DELETE' })
      setMsg(r.message)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  function pk() {
    return { vedas: 'veda_id', kandas: 'kanda_id', suktas: 'sukta_id',
      rishis: 'rishi_id', deities: 'deity_id', themes: 'theme_id',
      mantras: 'mantra_id' }[entity]
  }

  async function loadTags() {
    setMsg(''); setError('')
    try {
      const data = await api(`/admin/mantras/${tagMantra}/themes`)
      setTags(data.rows)
    } catch (err) {
      setError(err.message)
    }
  }

  async function addTag() {
    setMsg(''); setError('')
    try {
      const r = await api(`/admin/mantras/${tagMantra}/themes`,
        { method: 'POST', body: { theme_id: Number(tagTheme) } })
      setMsg(r.message)
      await loadTags()
    } catch (err) {
      setError(err.message)
    }
  }

  async function removeTag(themeId) {
    setMsg(''); setError('')
    try {
      const r = await api(`/admin/mantras/${tagMantra}/themes/${themeId}`,
        { method: 'DELETE' })
      setMsg(r.message)
      await loadTags()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Manage Data</h1>
      <p className="muted">
        Admin is the only role with DELETE. Foreign keys use ON DELETE
        RESTRICT - a protected row answers with a readable error.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>

      <div className="toolbar">
        <div className="field" style={{ maxWidth: 220 }}>
          <label>Table</label>
          <select value={entity} onChange={(e) => setEntity(e.target.value)}>
            {ENTITIES.map(([k, label]) => (
              <option key={k} value={k}>{label}</option>))}
          </select>
        </div>
      </div>

      <table className="data">
        <thead>
          <tr>
            {fields.map((f) => <th key={f}>{f.replace(/_/g, ' ')}</th>)}
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row[pk()]}>
              {editing && editing[pk()] === row[pk()] ? (
                <>
                  {fields.map((f) => (
                    <td key={f}>
                      <input value={editing[f] ?? ''}
                        onChange={(e) => setEditing({ ...editing,
                          [f]: e.target.value })} />
                    </td>
                  ))}
                  <td>
                    <button className="small" onClick={saveEdit}>Save</button>{' '}
                    <button className="secondary small"
                      onClick={() => setEditing(null)}>Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  {fields.map((f) => <td key={f}>{row[f]}</td>)}
                  <td>
                    <button className="secondary small"
                      onClick={() => setEditing({ ...row })}>Edit</button>{' '}
                    <button className="danger small"
                      onClick={() => del(row)}>Delete</button>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="divider"><span>❖ ❖ ❖</span></div>
      <h2>Add a new {entity.replace(/s$/, '')}</h2>
      <form onSubmit={add} className="card">
        <div className="form-row">
          {fields.map((f) => (
            <div className="field" key={f}>
              <label>{f.replace(/_/g, ' ')}</label>
              <input required value={form[f] ?? ''}
                onChange={(e) => setForm({ ...form, [f]: e.target.value })} />
            </div>
          ))}
        </div>
        <button type="submit">Add</button>
      </form>

      <div className="divider"><span>❖ ❖ ❖</span></div>
      <h2>Tag a Mantra with a Theme</h2>
      <div className="card">
        <div className="form-row">
          <div className="field" style={{ maxWidth: 160 }}>
            <label>Mantra ID</label>
            <input type="number" min="1" value={tagMantra}
              onChange={(e) => setTagMantra(e.target.value)} />
          </div>
          <div className="field">
            <label>Theme</label>
            <select value={tagTheme}
              onChange={(e) => setTagTheme(e.target.value)}>
              <option value="">choose…</option>
              {(entity === 'themes' ? rows : []).map((t) => (
                <option key={t.theme_id} value={t.theme_id}>
                  {t.theme_name}</option>))}
            </select>
          </div>
          <div style={{ alignSelf: 'end' }}>
            <button onClick={loadTags} disabled={!tagMantra}>List tags</button>{' '}
            <button onClick={addTag} disabled={!tagMantra || !tagTheme}>
              Assign
            </button>
          </div>
        </div>
        {tags && (
          <div className="tags" style={{ marginTop: '0.6rem' }}>
            {tags.length === 0 && <span className="muted">No themes on
              this Mantra.</span>}
            {tags.map((t) => (
              <span key={t.theme_id} className="tag theme">
                {t.theme_name}{' '}
                <button className="danger small"
                  onClick={() => removeTag(t.theme_id)}>×</button>
              </span>
            ))}
          </div>
        )}
        {entity !== 'themes' && (
          <p className="muted">Switch the table above to <b>Themes</b> to
            populate the dropdown.</p>
        )}
      </div>
    </>
  )
}

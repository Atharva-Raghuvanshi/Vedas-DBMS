import { useEffect, useState } from 'react'
import { api } from '../api.js'
import BarChart from '../components/BarChart.jsx'
import { ErrorBanner } from '../components/Banners.jsx'

const REPORTS = [
  ['mantras_per_veda', 'Mantras per Veda', true],
  ['mantras_per_rishi', 'Mantras per Rishi', true],
  ['mantras_per_deity', 'Mantras per Deity', true],
  ['translations_per_translator', 'Translations per Translator', true],
  ['suktas_without_translation', 'Suktas with no translation (LEFT JOIN)',
    false],
  ['structure_per_veda', 'Kanda / Sukta / Mantra summary per Veda', false],
]

/** Admin reports: the six queries, tables plus CSS bar charts. */
export default function AdminReportsPage() {
  const [key, setKey] = useState(REPORTS[0][0])
  const [rows, setRows] = useState(null)
  const [error, setError] = useState('')

  async function load(k = key) {
    setError('')
    try {
      const data = await api(`/admin/reports/${k}`)
      setRows(data.rows)
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { load(REPORTS[0][0]) }, [])

  function pick(e) {
    const k = e.target.value
    setKey(k)
    load(k)
  }

  const showBars = REPORTS.find(([k]) => k === key)?.[2]
  const cols = rows && rows[0] ? Object.keys(rows[0]) : []

  return (
    <>
      <h1>Reports</h1>
      <ErrorBanner>{error}</ErrorBanner>
      <div className="toolbar">
        <div className="field" style={{ maxWidth: 380 }}>
          <label>Report</label>
          <select value={key} onChange={pick}>
            {REPORTS.map(([k, label]) => (
              <option key={k} value={k}>{label}</option>))}
          </select>
        </div>
      </div>

      {rows && showBars && (
        <div className="card">
          <BarChart rows={rows.filter((r) => r.value !== undefined)} />
        </div>
      )}

      {rows && (
        <table className="data">
          <thead>
            <tr>{cols.map((c) => <th key={c}>{c.replace(/_/g, ' ')}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                {cols.map((c) => <td key={c}>{r[c] ?? '—'}</td>)}
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={cols.length} className="muted">
                No rows.</td></tr>)}
          </tbody>
        </table>
      )}
    </>
  )
}

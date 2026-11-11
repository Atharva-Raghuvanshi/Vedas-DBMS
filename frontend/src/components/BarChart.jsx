/** Simple horizontal bar chart: rows = [{label, value}]. Pure CSS bars. */
export default function BarChart({ rows, valueKey = 'value' }) {
  const max = Math.max(1, ...rows.map((r) => Number(r[valueKey]) || 0))
  return (
    <div className="bars">
      {rows.map((r, i) => (
        <div className="bar-row" key={i}>
          <span className="bar-label">{r.label}</span>
          <span className="bar-track">
            <span className="bar-fill"
              style={{ width: `${(Number(r[valueKey]) / max) * 100}%` }} />
          </span>
          <span className="bar-value">{r[valueKey]}</span>
        </div>
      ))}
    </div>
  )
}

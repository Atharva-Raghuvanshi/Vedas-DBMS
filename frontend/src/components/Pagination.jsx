/** Prev / 1 2 3 ... / Next pagination (same behaviour as the Streamlit app). */
export default function Pagination({ page, pages, onPage }) {
  if (pages <= 1) return null
  const nums = pages <= 10
    ? Array.from({ length: pages }, (_, i) => i + 1)
    : []   // too many: show only Prev/Next
  return (
    <div className="pager">
      <button className="secondary" disabled={page <= 1}
        onClick={() => onPage(page - 1)}>◀ Prev</button>
      {nums.map((p) => (
        <button key={p} className={p === page ? 'current' : 'secondary'}
          onClick={() => onPage(p)}>{p}</button>
      ))}
      <button className="secondary" disabled={page >= pages}
        onClick={() => onPage(page + 1)}>Next ▶</button>
      <span className="muted">Page {page} of {pages}</span>
    </div>
  )
}

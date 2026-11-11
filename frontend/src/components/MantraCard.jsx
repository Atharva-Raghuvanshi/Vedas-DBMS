import { api } from '../api.js'

/** One Mantra: Sanskrit on top, IAST in italics beneath, then the
 * translation, with Rishi / Deity / Metre / themes as small tags. */
export default function MantraCard({ m, actions }) {
  return (
    <article className="mantra-card">
      {m.sanskrit_text ? (
        <div className="sanskrit">{m.sanskrit_text}</div>
      ) : (
        <div className="no-sanskrit">[no Sanskrit text in the source
          dataset - translation only]</div>
      )}
      {m.iast_text && <div className="iast">{m.iast_text}</div>}
      {m.translation && <p className="translation">{m.translation}</p>}
      <div className="tags">
        <span className="tag rishi">Ṛṣi: {m.rishi_name}</span>
        <span className="tag deity">Devatā: {m.deity_name}</span>
        {m.metre && <span className="tag metre">{m.metre}</span>}
        {m.themes && m.themes.split(', ').filter(Boolean).map((t) => (
          <span key={t} className="tag theme">{t}</span>
        ))}
        <span className="tag">
          {m.veda_name} · {m.kanda_name} · {m.sukta_number}.{m.mantra_number}
        </span>
        <span className="tag">#{m.mantra_id}</span>
      </div>
      {actions && <div style={{ marginTop: '0.6rem' }}>{actions}</div>}
    </article>
  )
}

/** Small hook-style helpers shared by pages. */
export async function loadOptions(kind) {
  const rows = await api(`/options/${kind}`)
  return rows
}

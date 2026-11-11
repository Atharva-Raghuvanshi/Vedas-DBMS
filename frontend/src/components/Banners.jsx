/** Readable message banners - errors from the API land here verbatim. */
export function ErrorBanner({ children }) {
  if (!children) return null
  return <div className="banner error">⚠ {children}</div>
}

export function OkBanner({ children }) {
  if (!children) return null
  return <div className="banner ok">✓ {children}</div>
}

export function InfoBanner({ children }) {
  if (!children) return null
  return <div className="banner info">❖ {children}</div>
}

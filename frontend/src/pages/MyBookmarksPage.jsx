import { useEffect, useState } from 'react'
import { api } from '../api.js'
import MantraCard from '../components/MantraCard.jsx'
import { ErrorBanner, OkBanner } from '../components/Banners.jsx'

/** My Bookmarks: list own bookmarks, remove with one click. */
export default function MyBookmarksPage() {
  const [rows, setRows] = useState([])
  const [uid, setUid] = useState(null)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  async function load() {
    try {
      const data = await api('/student/bookmarks')
      setRows(data.rows)
      setUid(data.user_id)
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { load() }, [])

  async function remove(mantra_id) {
    setMsg(''); setError('')
    try {
      const r = await api(`/student/bookmarks/${mantra_id}`,
        { method: 'DELETE' })
      setMsg(r.message)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>My Bookmarks</h1>
      <p className="muted">
        Bookmarks of user #{uid}, listed through{' '}
        <code>v_student_bookmarks</code>.
      </p>
      <ErrorBanner>{error}</ErrorBanner>
      <OkBanner>{msg}</OkBanner>
      {rows.length === 0 && <p>No bookmarks yet - add some from the Search
        page.</p>}
      {rows.map((m) => (
        <MantraCard key={m.mantra_id} m={m}
          actions={
            <button className="danger small"
              onClick={() => remove(m.mantra_id)}>
              Remove bookmark
            </button>
          } />
      ))}
    </>
  )
}

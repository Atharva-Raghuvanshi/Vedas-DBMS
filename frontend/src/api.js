// Thin fetch wrapper: attaches the bearer token, parses JSON, and turns
// error responses into thrown Error objects the pages can show directly.

const TOKEN_KEY = 'vedas_token'
const AUTH_KEY = 'vedas_auth'

export function saveAuth(info) {
  localStorage.setItem(TOKEN_KEY, info.token)
  localStorage.setItem(AUTH_KEY, JSON.stringify(info))
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(AUTH_KEY)
}

export function getAuth() {
  const raw = localStorage.getItem(AUTH_KEY)
  if (!raw || !localStorage.getItem(TOKEN_KEY)) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export async function api(path, { method = 'GET', body } = {}) {
  const headers = {}
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) headers['Authorization'] = 'Bearer ' + token
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let res
  try {
    res = await fetch('/api' + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    // network-level failure (backend down) - never a blank screen
    throw new Error('Cannot reach the server - is the Flask backend running?')
  }

  let data = null
  try {
    data = await res.json()
  } catch {
    data = {}
  }
  if (!res.ok) {
    const err = new Error(data.message || `Request failed (${res.status})`)
    err.status = res.status
    throw err
  }
  return data
}

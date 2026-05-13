// Lightweight wrapper around localStorage/sessionStorage for safer access.
export function getLocal(key) {
  try {
    const raw = localStorage.getItem(key)
    return raw === null ? null : JSON.parse(raw)
  } catch (e) {
    return localStorage.getItem(key)
  }
}

export function setLocal(key, value) {
  try {
    if (typeof value === 'string') {
      localStorage.setItem(key, value)
    } else {
      localStorage.setItem(key, JSON.stringify(value))
    }
  } catch (e) {
    // best-effort no throw
  }
}

export function removeLocal(key) {
  try { localStorage.removeItem(key) } catch (e) {}
}

export function getSession(key) {
  try {
    const raw = sessionStorage.getItem(key)
    return raw === null ? null : JSON.parse(raw)
  } catch (e) {
    return sessionStorage.getItem(key)
  }
}

export function setSession(key, value) {
  try {
    if (typeof value === 'string') {
      sessionStorage.setItem(key, value)
    } else {
      sessionStorage.setItem(key, JSON.stringify(value))
    }
  } catch (e) {}
}

export function removeSession(key) {
  try { sessionStorage.removeItem(key) } catch (e) {}
}

const storage = {
  getLocal, setLocal, removeLocal, getSession, setSession, removeSession
}

export default storage

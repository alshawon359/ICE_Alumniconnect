import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { useLocation, useNavigate, useNavigationType } from 'react-router-dom'

const STORAGE_KEY = 'navigation_history_stack_v1'

const NavigationHistoryContext = createContext(null)

function readSessionStack() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch (err) {
    return []
  }
}

function writeSessionStack(stack) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stack))
  } catch (err) {
    // ignore
  }
}

export function NavigationHistoryProvider({ children, persist = true, debounceMs = 150 }) {
  const location = useLocation()
  const navigate = useNavigate()
  const navType = useNavigationType()

  const [stack, setStack] = useState(() => (persist ? readSessionStack() : []))

  // refs to keep stable between renders
  const prevLocationRef = useRef(location)
  const saveTimerRef = useRef(null)

  // helper to snapshot current page state
  const snapshotCurrent = useCallback((loc = location, extraState = {}) => {
    const entry = {
      pathname: loc.pathname,
      search: loc.search || '',
      key: loc.key || `${loc.pathname}${loc.search}`,
      timestamp: Date.now(),
      scrollY: typeof window !== 'undefined' ? window.scrollY : 0,
      state: extraState || {},
    }

    // collect simple form values (named inputs) and store under state.formValues
    try {
      const values = {}
      const inputs = document.querySelectorAll('input[name], textarea[name], select[name]')
      inputs.forEach((el) => {
        const name = el.getAttribute('name')
        if (!name) return
        if (el.type === 'checkbox' || el.type === 'radio') {
          if (el.checked) values[name] = el.value
        } else {
          values[name] = el.value
        }
      })
      entry.state = { ...entry.state, formValues: values }
    } catch (err) {
      // ignore DOM access errors during SSR or unusual env
    }

    return entry
  }, [location])

  // push entry into stack (debounced write)
  const pushEntry = useCallback((entry) => {
    setStack((prev) => {
      const next = [...prev, entry]
      if (persist) {
        if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
        saveTimerRef.current = setTimeout(() => writeSessionStack(next), debounceMs)
      }
      return next
    })
  }, [persist, debounceMs])

  const popEntry = useCallback(() => {
    let popped = null
    setStack((prev) => {
      if (!prev || prev.length === 0) return prev
      const next = prev.slice(0, prev.length - 1)
      popped = prev[prev.length - 1]
      if (persist) writeSessionStack(next)
      return next
    })
    return popped
  }, [persist])

  const clearStack = useCallback(() => {
    setStack([])
    if (persist) writeSessionStack([])
  }, [persist])

  // go back: pop and navigate to popped entry (restore state)
  const goBack = useCallback(() => {
    let popped = null
    let nextStack = null
    setStack((prev) => {
      if (!prev || prev.length === 0) {
        nextStack = prev
        return prev
      }
      nextStack = prev.slice(0, prev.length - 1)
      popped = prev[prev.length - 1]
      if (persist) writeSessionStack(nextStack)
      return nextStack
    })

    if (!popped) {
      navigate(-1)
      return
    }

    // navigate to popped location and pass its stored state
    const url = popped.pathname + (popped.search || '')
    navigate(url, { state: popped.state })
    // restore scroll and form values after short delay to allow page render
    setTimeout(() => {
      try {
        if (typeof window !== 'undefined') window.scrollTo(0, popped.scrollY || 0)
        const fv = popped.state?.formValues || {}
        Object.entries(fv).forEach(([name, value]) => {
          const el = document.querySelector(`[name="${name}"]`)
          if (el) el.value = value
        })
      } catch (err) {}
    }, 20)
  }, [navigate, persist])

  // On location change: decide whether to push previous location snapshot
  useEffect(() => {
    const prev = prevLocationRef.current
    // when navigation type is PUSH, we came from prev -> now; push prev state
    if (navType === 'PUSH' && prev) {
      // snapshot previous location and push
      const entry = snapshotCurrent(prev)
      pushEntry(entry)
    }

    // If nav type is REPLACE or POP we do not automatically push

    prevLocationRef.current = location
  }, [location, navType, pushEntry, snapshotCurrent])

  // On mount: if persisted stack exists, ensure it is loaded
  useEffect(() => {
    if (!persist) return
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY)
      if (raw) setStack(JSON.parse(raw))
    } catch (err) {}
  }, [persist])

  // Context value
  const value = {
    stack,
    pushEntry,
    popEntry,
    goBack,
    clearStack,
    snapshotCurrent,
  }

  return (
    <NavigationHistoryContext.Provider value={value}>{children}</NavigationHistoryContext.Provider>
  )
}

export function useNavigationHistoryContext() {
  const ctx = useContext(NavigationHistoryContext)
  if (!ctx) throw new Error('useNavigationHistoryContext must be used within NavigationHistoryProvider')
  return ctx
}

export default NavigationHistoryContext

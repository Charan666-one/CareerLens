import { useCallback, useEffect, useState } from "react"

// Roadmap completion is progress the user builds over weeks, so unlike the
// per-session pipeline results it lives in localStorage and is keyed by
// target role - switching roles keeps each path's progress separate, and it
// survives logout.
const KEY = "careerlens-roadmap-progress"

type ProgressStore = Record<string, string[]> // role -> completed skill names

function readStore(): ProgressStore {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as ProgressStore) : {}
  } catch {
    return {}
  }
}

function writeStore(store: ProgressStore) {
  localStorage.setItem(KEY, JSON.stringify(store))
}

export function useRoadmapProgress(role: string) {
  const [completed, setCompleted] = useState<Set<string>>(() => new Set(readStore()[role] ?? []))

  // Re-hydrate when the target role changes (the picker can switch it).
  useEffect(() => {
    setCompleted(new Set(readStore()[role] ?? []))
  }, [role])

  const persist = useCallback(
    (next: Set<string>) => {
      const store = readStore()
      store[role] = [...next]
      writeStore(store)
      setCompleted(next)
    },
    [role]
  )

  const complete = useCallback(
    (name: string) => {
      setCompleted((prev) => {
        const next = new Set(prev)
        next.add(name)
        const store = readStore()
        store[role] = [...next]
        writeStore(store)
        return next
      })
    },
    [role]
  )

  const uncomplete = useCallback(
    (name: string) => {
      setCompleted((prev) => {
        const next = new Set(prev)
        next.delete(name)
        const store = readStore()
        store[role] = [...next]
        writeStore(store)
        return next
      })
    },
    [role]
  )

  const reset = useCallback(() => persist(new Set()), [persist])

  return { completed, complete, uncomplete, reset }
}

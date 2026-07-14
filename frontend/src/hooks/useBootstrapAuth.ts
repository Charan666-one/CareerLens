import { useEffect } from "react"
import { me } from "@/services/authApi"
import { useAuthStore } from "@/store/auth"
import { logoutAndReset } from "@/store/session"

// A page refresh keeps the token (localStorage) but loses `user` (never
// persisted) - this repopulates it once per app mount, and cleans up if
// the token turned out to be stale/invalid.
export function useBootstrapAuth() {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)

  useEffect(() => {
    if (!token || user) return
    me()
      .then(setUser)
      .catch(() => logoutAndReset())
  }, [token, user, setUser])
}

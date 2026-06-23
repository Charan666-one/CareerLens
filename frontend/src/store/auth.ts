import { create } from "zustand"

interface AuthState {
  token: string | null
  user: { id: string; name: string; email: string } | null
  setToken: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("token"),
  user: null,
  setToken: (token) => { localStorage.setItem("token", token); set({ token }) },
  logout: () => { localStorage.removeItem("token"); set({ token: null, user: null }) }
}))

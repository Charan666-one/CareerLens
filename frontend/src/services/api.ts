import axios from "axios"
import { logoutAndReset } from "@/store/session"

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000" })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Signing in is the one place a 401 is an expected answer rather than an
// expired session: POST /api/auth/login returns 401 for a wrong password.
// Redirecting on those would tear the login form down mid-render, so the
// user would see a blank flash instead of "Incorrect email or password".
const AUTH_PATHS = ["/api/auth/login", "/api/auth/register"]

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const url = error.config?.url ?? ""
      const isAuthAttempt = AUTH_PATHS.some((path) => url.includes(path))
      if (!isAuthAttempt) {
        // A 401 anywhere else means the token we sent is gone or expired.
        logoutAndReset()
        window.location.assign("/login")
      }
    }
    return Promise.reject(error)
  }
)

export default api

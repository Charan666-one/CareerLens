import api from "@/services/api"
import type { AuthTokenResponse, User } from "@/types"

export interface RegisterPayload {
  email: string
  password: string
  name: string
}

export interface LoginPayload {
  email: string
  password: string
}

export function register(payload: RegisterPayload) {
  return api.post<User>("/api/auth/register", payload).then((r) => r.data)
}

export function login(payload: LoginPayload) {
  return api.post<AuthTokenResponse>("/api/auth/login", payload).then((r) => r.data)
}

export function me() {
  return api.get<User>("/api/auth/me").then((r) => r.data)
}

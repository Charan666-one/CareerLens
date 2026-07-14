import axios from "axios"

export type NormalizedError =
  | { kind: "auth"; message: string }
  | { kind: "conflict"; message: string; missingPrerequisite: string }
  | { kind: "validation"; message: string }
  | { kind: "unknown"; message: string }

interface ConflictDetail {
  error: string
  missing_prerequisite: string
  message: string
}

export function normalizeApiError(err: unknown): NormalizedError {
  if (!axios.isAxiosError(err)) {
    return { kind: "unknown", message: "Something went wrong." }
  }

  const status = err.response?.status
  const detail = err.response?.data?.detail as string | ConflictDetail | undefined

  if (status === 401) {
    return { kind: "auth", message: typeof detail === "string" ? detail : "Please log in again." }
  }

  if (status === 409 && detail && typeof detail === "object") {
    return {
      kind: "conflict",
      message: detail.message ?? "A prior stage needs to run first.",
      missingPrerequisite: detail.missing_prerequisite,
    }
  }

  if (status === 400 || status === 413) {
    return { kind: "validation", message: typeof detail === "string" ? detail : "Invalid request." }
  }

  return { kind: "unknown", message: typeof detail === "string" ? detail : "Something went wrong." }
}

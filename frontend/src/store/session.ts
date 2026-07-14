import { useAuthStore } from "@/store/auth"
import { usePipelineStore } from "@/store/pipeline"

// Kept out of auth.ts to avoid a circular import between the two store
// files - both the logout button and the 401 response interceptor call
// this so a sign-out always clears both the session and any in-progress
// pipeline results together.
export function logoutAndReset() {
  useAuthStore.getState().logout()
  usePipelineStore.getState().reset()
}

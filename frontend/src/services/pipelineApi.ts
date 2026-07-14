import api from "@/services/api"
import type {
  ProfileResponse,
  RecommendationsResponse,
  ResumeScoreResponse,
  RoadmapResponse,
  SkillGapResponse,
  SuitabilityResponse,
  StrengthsResponse,
} from "@/types"

export function runProfile(file: File) {
  const form = new FormData()
  form.append("file", file)
  return api.post<ProfileResponse>("/api/pipeline/profile", form).then((r) => r.data)
}

export function runStrengths() {
  return api.post<StrengthsResponse>("/api/pipeline/strengths").then((r) => r.data)
}

export function runSuitability(targetRoles?: string[]) {
  return api
    .post<SuitabilityResponse>("/api/pipeline/suitability", { target_roles: targetRoles })
    .then((r) => r.data)
}

export function runSkillGap(targetRole: string) {
  return api
    .post<SkillGapResponse>("/api/pipeline/skill-gap", { target_role: targetRole })
    .then((r) => r.data)
}

export function runRoadmap() {
  return api.post<RoadmapResponse>("/api/pipeline/roadmap").then((r) => r.data)
}

export function runResumeScore(file: File) {
  const form = new FormData()
  form.append("file", file)
  return api.post<ResumeScoreResponse>("/api/pipeline/resume-score", form).then((r) => r.data)
}

export function runRecommendations() {
  return api.post<RecommendationsResponse>("/api/pipeline/recommendations").then((r) => r.data)
}

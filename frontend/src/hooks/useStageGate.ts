import { useShallow } from "zustand/react/shallow"
import { usePipelineStore, type StageStatus } from "@/store/pipeline"

export type PipelineStageKey =
  | "profile"
  | "strengths"
  | "suitability"
  | "skillGap"
  | "roadmap"
  | "resumeScore"
  | "recommendations"

// Static dependency graph, mirrors app/services/pipeline/state.py's
// prerequisite checks - lets the UI disable a stage's action and explain
// why *before* attempting a request, instead of waiting for a 409.
const PREREQUISITES: Record<PipelineStageKey, { key: PipelineStageKey; label: string }[]> = {
  profile: [],
  strengths: [{ key: "profile", label: "Profile" }],
  suitability: [{ key: "profile", label: "Profile" }],
  skillGap: [{ key: "suitability", label: "Suitability" }],
  roadmap: [{ key: "skillGap", label: "Skill Gap" }],
  resumeScore: [],
  recommendations: [
    { key: "profile", label: "Profile" },
    { key: "strengths", label: "Strengths" },
    { key: "suitability", label: "Suitability" },
    { key: "skillGap", label: "Skill Gap" },
    { key: "roadmap", label: "Roadmap" },
    { key: "resumeScore", label: "Resume Score" },
  ],
}

export interface StageGate {
  ready: boolean
  missing: string[]
  status: StageStatus
}

export function useStageGate(key: PipelineStageKey): StageGate {
  return usePipelineStore(
    useShallow((s) => {
      const missing = PREREQUISITES[key].filter((p) => s[p.key].status !== "success").map((p) => p.label)
      return { ready: missing.length === 0, missing, status: s[key].status }
    })
  )
}

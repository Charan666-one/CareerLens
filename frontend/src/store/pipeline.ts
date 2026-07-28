import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"
import * as pipelineApi from "@/services/pipelineApi"
import { normalizeApiError, type NormalizedError } from "@/services/errors"
import type {
  ProfileResponse,
  RecommendationsResponse,
  ResumeScoreResponse,
  RoadmapResponse,
  SkillGapResponse,
  SuitabilityResponse,
  StrengthsResponse,
} from "@/types"

export type StageStatus = "idle" | "loading" | "success" | "error"

export interface StageSlice<T> {
  data: T | null
  status: StageStatus
  error: NormalizedError | null
}

function idleSlice<T>(): StageSlice<T> {
  return { data: null, status: "idle", error: null }
}

// Bumped by reset() (called on logout and on a 401). A stage run captures
// the epoch when it starts; if reset() happens while a request is in flight,
// the epoch no longer matches when the response lands, so the completion is
// dropped instead of writing one user's data into the next user's freshly
// reset (and persisted) store.
let sessionEpoch = 0

const STAGE_KEYS = [
  "profile",
  "strengths",
  "suitability",
  "skillGap",
  "roadmap",
  "resumeScore",
  "recommendations",
] as const

type StageKey = (typeof STAGE_KEYS)[number]

interface PipelineState {
  profile: StageSlice<ProfileResponse>
  strengths: StageSlice<StrengthsResponse>
  suitability: StageSlice<SuitabilityResponse>
  skillGap: StageSlice<SkillGapResponse>
  roadmap: StageSlice<RoadmapResponse>
  resumeScore: StageSlice<ResumeScoreResponse>
  recommendations: StageSlice<RecommendationsResponse>

  selectedTargetRole: string | null
  setTargetRole: (role: string) => Promise<void>

  runProfile: (file: File) => Promise<void>
  runStrengths: () => Promise<void>
  runSuitability: (targetRoles?: string[]) => Promise<void>
  runSkillGap: (targetRole: string) => Promise<void>
  runRoadmap: () => Promise<void>
  runResumeScore: (file: File) => Promise<void>
  runRecommendations: () => Promise<void>
  maybeRunRecommendations: () => Promise<void>

  reset: () => void
}

export const usePipelineStore = create<PipelineState>()(
  persist(
    (set, get) => {
      // Generic stage-runner: every stage follows the same
      // loading/success/error lifecycle, so this is the one place that
      // logic lives instead of being hand-written 7 times. The `as any`
      // on the `set` calls is a narrow, contained cast - TypeScript can't
      // prove a dynamically-keyed partial update matches a record of
      // differently-typed slices, even though each call site here is
      // correct by construction.
      function runStage<T, A extends unknown[]>(
        key: StageKey,
        call: (...args: A) => Promise<T>,
        onSuccess?: (data: T) => void | Promise<void>
      ) {
        return async (...args: A) => {
          const startedAt = sessionEpoch
          const isCurrent = () => sessionEpoch === startedAt
          set((s) => ({ [key]: { ...s[key], status: "loading", error: null } }) as any)
          try {
            const data = await call(...args)
            // A logout/401 between the request and its response invalidates
            // this write - dropping it keeps a stale response from
            // repopulating (and re-persisting) a store that was just reset
            // for a different session.
            if (!isCurrent()) return
            set(() => ({ [key]: { data, status: "success", error: null } }) as any)
            await onSuccess?.(data)
          } catch (err) {
            if (!isCurrent()) return
            const error = normalizeApiError(err)
            set((s) => ({ [key]: { ...s[key], status: "error", error } }) as any)
          }
        }
      }

      const runSuitability = runStage<SuitabilityResponse, [targetRoles?: string[]]>(
        "suitability",
        pipelineApi.runSuitability,
        async (data) => {
          if (data.roles.length === 0) return
          const top = [...data.roles].sort((a, b) => b.final_score - a.final_score)[0]
          set({ selectedTargetRole: top.role_title })
          await get().runSkillGap(top.role_title)
        }
      )

      const runSkillGap = runStage<SkillGapResponse, [targetRole: string]>(
        "skillGap",
        pipelineApi.runSkillGap,
        async () => {
          await get().runRoadmap()
        }
      )

      const runRoadmap = runStage<RoadmapResponse, []>("roadmap", pipelineApi.runRoadmap, async () => {
        await get().maybeRunRecommendations()
      })

      const runResumeScore = runStage<ResumeScoreResponse, [file: File]>(
        "resumeScore",
        pipelineApi.runResumeScore,
        async () => {
          await get().maybeRunRecommendations()
        }
      )

      const runRecommendations = runStage<RecommendationsResponse, []>(
        "recommendations",
        pipelineApi.runRecommendations
      )

      return {
        profile: idleSlice(),
        strengths: idleSlice(),
        suitability: idleSlice(),
        skillGap: idleSlice(),
        roadmap: idleSlice(),
        resumeScore: idleSlice(),
        recommendations: idleSlice(),

        selectedTargetRole: null,
        setTargetRole: async (role: string) => {
          set({ selectedTargetRole: role, recommendations: idleSlice() })
          await runSkillGap(role)
        },

        runProfile: runStage<ProfileResponse, [file: File]>("profile", pipelineApi.runProfile, async () => {
          await get().runStrengths()
          await get().runSuitability()
        }),
        runStrengths: runStage<StrengthsResponse, []>("strengths", pipelineApi.runStrengths),
        runSuitability,
        runSkillGap,
        runRoadmap,
        runResumeScore,
        runRecommendations,

        maybeRunRecommendations: async () => {
          const s = get()
          const prereqsDone =
            s.profile.status === "success" &&
            s.strengths.status === "success" &&
            s.suitability.status === "success" &&
            s.skillGap.status === "success" &&
            s.roadmap.status === "success" &&
            s.resumeScore.status === "success"
          if (prereqsDone && s.recommendations.status === "idle") {
            await runRecommendations()
          }
        },

        reset: () => {
          // Invalidate any in-flight stage runs before wiping state, so
          // their responses can't land afterwards and re-persist this
          // session's data for whoever logs in next on this tab.
          sessionEpoch += 1
          set({
            profile: idleSlice(),
            strengths: idleSlice(),
            suitability: idleSlice(),
            skillGap: idleSlice(),
            roadmap: idleSlice(),
            resumeScore: idleSlice(),
            recommendations: idleSlice(),
            selectedTargetRole: null,
          })
          // Setting idle above already re-persists an empty snapshot, but
          // clear the key outright so nothing lingers even momentarily.
          usePipelineStore.persist.clearStorage()
        },
      }
    },
    {
      name: "careerlens-pipeline",
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => {
        const persisted: Record<string, unknown> = { selectedTargetRole: state.selectedTargetRole }
        for (const key of STAGE_KEYS) persisted[key] = { data: state[key].data }
        return persisted
      },
      merge: (persisted, current) => {
        const merged = { ...current }
        const persistedRecord = (persisted ?? {}) as Record<string, unknown>
        for (const key of STAGE_KEYS) {
          const data = (persistedRecord[key] as { data?: unknown } | undefined)?.data
          if (data !== undefined && data !== null) {
            ;(merged as any)[key] = { data, status: "success", error: null }
          }
        }
        // partialize persists this too, but it isn't a STAGE_KEY, so without
        // restoring it here it always came back null - leaving the skill-gap
        // heading naming a role while the picker rendered blank (no <option>
        // matches "").
        const role = persistedRecord.selectedTargetRole
        if (typeof role === "string") merged.selectedTargetRole = role
        return merged
      },
    }
  )
)

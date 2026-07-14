import RecommendationCard from "@/components/pipeline/RecommendationCard"
import { usePipelineStore } from "@/store/pipeline"

export default function RecommendationsSection() {
  const recommendations = usePipelineStore((s) => s.recommendations)

  if (recommendations.status === "idle") return null

  const recs = recommendations.data?.recommendations ?? []
  const eligible = recs.filter((r) => r.missing_skills.length === 0)
  const gap = recs.filter((r) => r.missing_skills.length > 0)
  // Eligible-first, then by score within each group.
  const sorted = [...eligible, ...gap].sort((a, b) => {
    const aEligible = a.missing_skills.length === 0
    const bEligible = b.missing_skills.length === 0
    if (aEligible !== bEligible) return aEligible ? -1 : 1
    return b.final_score - a.final_score
  })

  return (
    <section className="mb-[52px]">
      <div className="flex items-baseline justify-between gap-5 mb-[18px]">
        <div>
          <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
            Stage 7 — Recommendations
          </span>
          <h2 className="font-display text-xl text-balance">Your recommended routes</h2>
        </div>
        <p className="text-[0.86rem] text-text-dim max-w-[46ch]">
          Ranked on what you can do today, not just what you're headed toward — every gap is named, not
          hidden.
        </p>
      </div>

      {recommendations.status === "loading" && (
        <p className="text-sm text-text-dim">Assembling recommendations…</p>
      )}
      {recommendations.status === "error" && recommendations.error && (
        <p className="text-warn text-sm">{recommendations.error.message}</p>
      )}

      {recommendations.data && (
        <>
          <div className="flex gap-5 mb-4 text-[0.82rem] text-text-dim font-mono">
            <span>
              <b className="font-body font-semibold text-good">{eligible.length}</b> eligible now
            </span>
            <span>
              <b className="font-body font-semibold text-warn">{gap.length}</b> within reach, skills pending
            </span>
          </div>
          <div className="flex flex-col gap-3">
            {sorted.map((rec) => (
              <RecommendationCard key={rec.job_id} rec={rec} />
            ))}
          </div>
        </>
      )}
    </section>
  )
}

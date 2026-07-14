import SuitabilityHeroCard from "@/components/pipeline/SuitabilityHeroCard"
import SuitabilityRoleRow from "@/components/pipeline/SuitabilityRoleRow"
import { usePipelineStore } from "@/store/pipeline"

export default function SuitabilitySection() {
  const suitability = usePipelineStore((s) => s.suitability)

  if (suitability.status === "idle") return null

  return (
    <section className="mb-[52px]">
      <div className="flex items-baseline justify-between gap-5 mb-[18px]">
        <div>
          <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
            Stage 3 — Suitability
          </span>
          <h2 className="font-display text-xl text-balance">How you measure up, by role</h2>
        </div>
        <p className="text-[0.86rem] text-text-dim max-w-[46ch]">
          Every score is three readings, not one — text closeness to the role, graph distance across your
          skills, and market pull. Nothing here is a black box.
        </p>
      </div>

      {suitability.status === "loading" && <p className="text-sm text-text-dim">Scoring roles…</p>}
      {suitability.status === "error" && suitability.error && (
        <p className="text-warn text-sm">{suitability.error.message}</p>
      )}

      {suitability.data && suitability.data.roles.length > 0 && (
        <div className="grid md:grid-cols-[1.1fr_1fr] gap-[18px]">
          <SuitabilityHeroCard role={suitability.data.roles[0]} weights={suitability.data.weights} />
          <div className="flex flex-col gap-px bg-stone-line border border-stone-line rounded overflow-hidden">
            {suitability.data.roles.slice(1, 4).map((role) => (
              <SuitabilityRoleRow key={role.role_title} role={role} weights={suitability.data!.weights} />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

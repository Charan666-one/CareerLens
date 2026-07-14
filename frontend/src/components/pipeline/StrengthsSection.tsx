import Card from "@/components/ui/Card"
import Pill from "@/components/ui/Pill"
import { usePipelineStore } from "@/store/pipeline"

export default function StrengthsSection() {
  const strengths = usePipelineStore((s) => s.strengths)

  if (strengths.status === "idle") return null

  return (
    <section className="mb-[52px]">
      <div className="flex items-baseline justify-between gap-5 mb-4">
        <div>
          <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
            Stage 2 — Strengths
          </span>
          <h2 className="font-display text-xl text-balance">Where you're strong, where you're thin</h2>
        </div>
        <p className="text-[0.86rem] text-text-dim max-w-[46ch]">
          Strengths need two or more skills in a category at solid market demand; weaknesses name the
          highest-demand skills you're missing there.
        </p>
      </div>

      {strengths.status === "loading" && <p className="text-sm text-text-dim">Analyzing strengths…</p>}
      {strengths.status === "error" && strengths.error && (
        <p className="text-warn text-sm">{strengths.error.message}</p>
      )}

      {strengths.data && (
        <div className="grid md:grid-cols-2 gap-4">
          <Card className="p-5" accent="good">
            <h3 className="font-display text-base mb-3">Strengths</h3>
            {strengths.data.strengths.length === 0 ? (
              <p className="text-sm text-text-dim">No category has two or more high-demand skills yet.</p>
            ) : (
              <ul className="flex flex-col gap-2.5">
                {strengths.data.strengths.map((s) => (
                  <li key={s.category} className="flex items-center justify-between text-sm">
                    <span className="capitalize">{s.category}</span>
                    <span className="font-mono text-text-dim">
                      {s.skill_count} skills · {Math.round(s.avg_market_demand * 100)}% demand
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card className="p-5" accent="warn">
            <h3 className="font-display text-base mb-3">Weaknesses</h3>
            {strengths.data.weaknesses.length === 0 ? (
              <p className="text-sm text-text-dim">No thin categories found.</p>
            ) : (
              <ul className="flex flex-col gap-3">
                {strengths.data.weaknesses.map((w) => (
                  <li key={w.category}>
                    <div className="text-sm capitalize mb-1.5">{w.category}</div>
                    <div className="flex gap-1.5 flex-wrap">
                      {w.missing_high_demand_skills.map((name) => (
                        <Pill key={name} variant="missing">
                          {name}
                        </Pill>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      )}
    </section>
  )
}

import Card from "@/components/ui/Card"
import Donut from "@/components/ui/Donut"
import Pill from "@/components/ui/Pill"
import type { RoleSuitability, SuitabilityWeights } from "@/types"

interface SuitabilityHeroCardProps {
  role: RoleSuitability
  weights: SuitabilityWeights
}

export default function SuitabilityHeroCard({ role, weights }: SuitabilityHeroCardProps) {
  return (
    <Card className="p-6 flex gap-6 items-center">
      <Donut
        segments={[
          { fraction: weights.score_text * role.score_text, colorVar: "var(--brass)" },
          { fraction: weights.score_graph * role.score_graph, colorVar: "var(--good)" },
        ]}
        centerValue={role.final_score.toFixed(2)}
        centerLabel="final"
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline justify-between gap-3">
          <span className="font-display text-xl">{role.role_title}</span>
          <span className="font-mono text-[0.95rem] text-brass-strong">{role.final_score.toFixed(4)}</span>
        </div>
        <div className="flex gap-4 mt-3.5 flex-wrap text-[0.76rem] text-text-dim">
          <span className="flex items-center gap-1.5">
            <span className="w-[9px] h-[9px] rounded-sm bg-brass inline-block" />
            text {role.score_text.toFixed(2)} × {weights.score_text}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-[9px] h-[9px] rounded-sm bg-good inline-block" />
            graph {role.score_graph.toFixed(2)} × {weights.score_graph}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-[9px] h-[9px] rounded-sm bg-stone-line border border-text-dim inline-block" />
            demand {role.score_demand.toFixed(2)} × {weights.score_demand}
          </span>
        </div>
        <div className="flex gap-1.5 flex-wrap mt-4">
          {role.matched_skills.map((name) => (
            <Pill key={name} variant="matched">
              {name}
            </Pill>
          ))}
          {role.missing_skills.map((name) => (
            <Pill key={name} variant="missing">
              {name}
            </Pill>
          ))}
        </div>
      </div>
    </Card>
  )
}

import SegmentedBar from "@/components/ui/SegmentedBar"
import type { RoleSuitability, SuitabilityWeights } from "@/types"

interface SuitabilityRoleRowProps {
  role: RoleSuitability
  weights: SuitabilityWeights
}

export default function SuitabilityRoleRow({ role, weights }: SuitabilityRoleRowProps) {
  return (
    <div className="bg-stone-raised px-[18px] py-3.5 flex flex-col gap-2">
      <div className="flex items-center justify-between gap-4">
        <span className="font-display text-[0.98rem]">{role.role_title}</span>
        <span className="font-mono text-[0.86rem] text-brass-strong">{role.final_score.toFixed(4)}</span>
      </div>
      <SegmentedBar
        segments={[
          { fraction: weights.score_text * role.score_text, colorClass: "bg-brass" },
          { fraction: weights.score_graph * role.score_graph, colorClass: "bg-good" },
          { fraction: weights.score_demand * role.score_demand, colorClass: "bg-[#b7b39f]" },
        ]}
      />
    </div>
  )
}

import ProgressBar from "@/components/ui/ProgressBar"
import type { SkillGapItem } from "@/types"

export default function SkillGapRow({ item }: { item: SkillGapItem }) {
  return (
    <div className="bg-stone-raised border border-stone-line rounded px-5 py-4">
      <div className="flex justify-between items-baseline">
        <span className="font-display text-[1.02rem]">{item.name}</span>
        <span className="font-mono text-[0.78rem] text-text-dim">≈ {item.avg_learn_weeks} weeks</span>
      </div>
      <div className="my-3">
        <ProgressBar fraction={item.importance_score} />
      </div>
      <div className="flex gap-[18px] flex-wrap text-[0.76rem] text-text-dim font-mono">
        <span>
          importance <b className="text-text font-semibold">{item.importance_score.toFixed(4)}</b>
        </span>
        <span>
          graph proximity <b className="text-text font-semibold">{item.graph_proximity.toFixed(2)}</b>
        </span>
        <span>
          market demand <b className="text-text font-semibold">{item.market_demand.toFixed(2)}</b>
        </span>
      </div>
    </div>
  )
}

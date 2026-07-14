import Card from "@/components/ui/Card"
import Pill from "@/components/ui/Pill"
import type { JobRecommendation } from "@/types"

export default function RecommendationCard({ rec }: { rec: JobRecommendation }) {
  const eligible = rec.missing_skills.length === 0

  return (
    <Card accent={eligible ? "good" : "warn"} className="p-5 pl-[23px] grid grid-cols-[auto_1fr_auto] gap-4 items-start">
      <div className="w-10 h-10 rounded-full bg-ink text-brass font-display flex items-center justify-center flex-none">
        {rec.company?.slice(0, 2) ?? "—"}
      </div>
      <div>
        <div className="flex items-baseline gap-2.5 flex-wrap">
          <span className="font-display text-[1.05rem]">{rec.title}</span>
          <span className="text-[0.8rem] text-text-dim">
            {rec.company}
            {rec.location ? ` · ${rec.location}` : ""}
          </span>
          <span
            className={`ml-auto inline-flex items-center gap-1.5 text-[0.68rem] tracking-wide uppercase px-2.5 py-1 rounded-full border ${
              eligible ? "text-good border-good/35" : "text-warn border-warn/35"
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${eligible ? "bg-good" : "bg-warn"}`} />
            {eligible ? "Eligible now" : `Missing ${rec.missing_skills.length} skill${rec.missing_skills.length > 1 ? "s" : ""}`}
          </span>
        </div>
        <p className="mt-2 text-[0.86rem] text-text-dim max-w-[62ch]">{rec.explanation}</p>
        <div className="flex gap-1.5 flex-wrap mt-3">
          {rec.matched_skills.map((name) => (
            <Pill key={name} variant="matched">
              {name}
            </Pill>
          ))}
          {rec.missing_skills.map((name) => (
            <Pill key={name} variant="missing">
              {name}
            </Pill>
          ))}
        </div>
        <a
          href="#"
          className={`inline-block mt-3 text-[0.76rem] font-mono border-b ${
            eligible ? "text-brass-strong border-brass/35" : "text-warn border-warn/35"
          }`}
        >
          {eligible ? "View role and apply →" : "See the roadmap for this gap →"}
        </a>
      </div>
      <div className="text-right whitespace-nowrap">
        <span className="block font-mono text-lg text-brass-strong">{rec.final_score.toFixed(4)}</span>
        <span className="text-[0.66rem] tracking-wide uppercase text-text-dim">final score</span>
      </div>
    </Card>
  )
}

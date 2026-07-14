import NodeBadge from "@/components/ui/NodeBadge"
import { usePipelineStore } from "@/store/pipeline"

export default function RoadmapPath() {
  const roadmap = usePipelineStore((s) => s.roadmap)

  if (roadmap.status === "idle") return null

  return (
    <section className="mb-[52px]">
      <div className="flex items-baseline justify-between gap-5 mb-[18px]">
        <div>
          <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
            Stage 5 — Roadmap
          </span>
          <h2 className="font-display text-xl text-balance">The charted route</h2>
        </div>
        <p className="text-[0.86rem] text-text-dim max-w-[46ch]">
          Sequenced by prerequisite depth first, then by importance — this is the order the graph actually
          recommends.
        </p>
      </div>

      {roadmap.status === "loading" && <p className="text-sm text-text-dim">Sequencing your route…</p>}
      {roadmap.status === "error" && roadmap.error && <p className="text-warn text-sm">{roadmap.error.message}</p>}

      {roadmap.data && (
        <>
          <div className="flex overflow-x-auto pb-1.5 -mx-1">
            {roadmap.data.sequenced_skills.map((skill, i) => (
              <div key={skill.name} className="flex-1 min-w-[190px] relative pr-6 px-1">
                {i < roadmap.data!.sequenced_skills.length - 1 && (
                  <div
                    className="absolute top-[17px] h-px"
                    style={{
                      left: 40,
                      right: -8,
                      backgroundImage:
                        "repeating-linear-gradient(to right, var(--brass) 0 6px, transparent 6px 11px)",
                    }}
                  />
                )}
                <div className="bg-stone-raised border border-stone-line rounded px-4 pt-4 pb-3.5">
                  <div className="mb-3">
                    <NodeBadge variant="plain">{skill.order}</NodeBadge>
                  </div>
                  <div className="font-display text-base mb-1">{skill.name}</div>
                  <div className="text-[0.76rem] text-text-dim font-mono">
                    {skill.avg_learn_weeks} wks · cumulative {skill.cumulative_weeks} wks
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-[18px] text-[0.82rem] text-text-dim font-mono">
            Total time to close every gap for this role:{" "}
            <b className="text-text font-semibold">{roadmap.data.total_estimated_weeks} weeks</b>
          </p>
        </>
      )}
    </section>
  )
}

import SkillGapRow from "@/components/pipeline/SkillGapRow"
import TargetRoleSelect from "@/components/pipeline/TargetRoleSelect"
import { usePipelineStore } from "@/store/pipeline"

export default function SkillGapSection() {
  const skillGap = usePipelineStore((s) => s.skillGap)

  if (skillGap.status === "idle") return null

  return (
    <section className="mb-[52px]">
      <div className="flex items-baseline justify-between gap-5 mb-[18px]">
        <div>
          <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
            Stage 4 — Skill Gap
          </span>
          <h2 className="font-display text-xl text-balance">
            Closing the distance to {skillGap.data?.target_role ?? "your target role"}
          </h2>
        </div>
        <p className="text-[0.86rem] text-text-dim max-w-[46ch]">
          Ranked by graph proximity to what you already know, market demand, and how the role's own
          postings talk about it.
        </p>
      </div>

      <TargetRoleSelect />

      {skillGap.status === "loading" && <p className="text-sm text-text-dim">Analyzing the gap…</p>}
      {skillGap.status === "error" && skillGap.error && (
        <p className="text-warn text-sm">{skillGap.error.message}</p>
      )}

      {skillGap.data && (
        <div className="flex flex-col gap-3.5">
          {skillGap.data.missing_skills.length === 0 ? (
            <p className="text-sm text-text-dim">No gap — every required skill for this role is covered.</p>
          ) : (
            skillGap.data.missing_skills.map((item) => <SkillGapRow key={item.name} item={item} />)
          )}
        </div>
      )}
    </section>
  )
}

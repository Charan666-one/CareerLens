import { useShallow } from "zustand/react/shallow"
import StatTile from "@/components/ui/StatTile"
import { usePipelineStore } from "@/store/pipeline"

export default function StatStrip() {
  const { profile, suitability, skillGap, resumeScore } = usePipelineStore(
    useShallow((s) => ({
      profile: s.profile.data,
      suitability: s.suitability.data,
      skillGap: s.skillGap.data,
      resumeScore: s.resumeScore.data,
    }))
  )

  if (!profile) return null

  const topRole = suitability?.roles[0]
  const skillNames = profile.extracted_skills.map((s) => s.name)

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-stone-line border border-stone-line rounded overflow-hidden mb-[52px]">
      <StatTile
        label="Skills extracted"
        value={profile.skill_count}
        sub={skillNames.length > 0 ? `${skillNames.slice(0, 3).join(" · ")}${skillNames.length > 3 ? ` +${skillNames.length - 3}` : ""}` : undefined}
      />
      <StatTile
        label="Top match"
        value={topRole ? `${Math.round(topRole.final_score * 100)}%` : "—"}
        sub={topRole?.role_title}
      />
      <StatTile
        label="Skills to close gap"
        value={skillGap ? skillGap.missing_skills.length : "—"}
        sub={
          skillGap && skillGap.missing_skills.length > 0
            ? `${skillGap.missing_skills[0].name} · ~${skillGap.missing_skills[0].avg_learn_weeks} wks`
            : undefined
        }
      />
      <StatTile
        label="Resume score"
        value={resumeScore ? resumeScore.overall_score : "—"}
        sub={resumeScore ? `clarity ${resumeScore.clarity_score} · impact ${resumeScore.impact_score}` : undefined}
      />
    </div>
  )
}

import { usePipelineStore } from "@/store/pipeline"

export default function TargetRoleSelect() {
  const roles = usePipelineStore((s) => s.suitability.data?.roles ?? [])
  const selected = usePipelineStore((s) => s.selectedTargetRole)
  const setTargetRole = usePipelineStore((s) => s.setTargetRole)

  if (roles.length === 0) return null

  return (
    <label className="flex items-center gap-2.5 text-sm mb-4">
      <span className="text-text-dim">Target role:</span>
      <select
        className="bg-stone-raised border border-stone-line rounded px-2.5 py-1.5 font-mono text-[0.85rem]"
        value={selected ?? ""}
        onChange={(e) => setTargetRole(e.target.value)}
      >
        {roles.map((r) => (
          <option key={r.role_title} value={r.role_title}>
            {r.role_title} — {r.final_score.toFixed(2)}
          </option>
        ))}
      </select>
    </label>
  )
}

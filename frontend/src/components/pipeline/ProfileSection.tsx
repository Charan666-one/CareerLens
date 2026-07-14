import Card from "@/components/ui/Card"
import FileDropzone from "@/components/ui/FileDropzone"
import { usePipelineStore } from "@/store/pipeline"

export default function ProfileSection() {
  const profile = usePipelineStore((s) => s.profile)
  const runProfile = usePipelineStore((s) => s.runProfile)

  if (profile.status === "success" && profile.data) {
    return (
      <Card className="flex items-center gap-4 px-5 py-4 mb-9">
        <div className="w-[34px] h-[34px] rounded-full bg-good/10 text-good flex items-center justify-center flex-none">
          ✓
        </div>
        <div className="min-w-0">
          <div className="font-mono text-sm truncate">{profile.data.summary}</div>
          <div className="text-[0.78rem] text-text-dim mt-0.5">
            {profile.data.skill_count} skills extracted
          </div>
        </div>
        <span className="ml-auto text-[0.72rem] tracking-wide uppercase text-good border border-good/35 rounded-full px-2.5 py-1">
          Analyzed
        </span>
      </Card>
    )
  }

  return (
    <div className="mb-9">
      <FileDropzone label="Upload your resume" onFile={runProfile} disabled={profile.status === "loading"} />
      {profile.status === "loading" && <p className="text-sm text-text-dim mt-2">Analyzing your resume…</p>}
      {profile.status === "error" && profile.error && (
        <p className="text-warn text-sm mt-2">{profile.error.message}</p>
      )}
    </div>
  )
}

import Card from "@/components/ui/Card"
import FileDropzone from "@/components/ui/FileDropzone"
import ProgressBar from "@/components/ui/ProgressBar"
import { usePipelineStore } from "@/store/pipeline"

export default function ResumeScoreCard() {
  const resumeScore = usePipelineStore((s) => s.resumeScore)
  const runResumeScore = usePipelineStore((s) => s.runResumeScore)

  return (
    <section className="mb-[52px]">
      <div className="mb-[18px]">
        <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
          Stage 6 — Resume Score
        </span>
        <h2 className="font-display text-xl text-balance">How the resume itself reads</h2>
        <p className="text-[0.86rem] text-text-dim mt-1">
          Independent of the rest of the pipeline — run it on any resume, anytime.
        </p>
      </div>

      {!resumeScore.data && (
        <FileDropzone
          label="Upload a resume to score"
          onFile={runResumeScore}
          disabled={resumeScore.status === "loading"}
        />
      )}
      {resumeScore.status === "loading" && <p className="text-sm text-text-dim mt-2">Scoring…</p>}
      {resumeScore.status === "error" && resumeScore.error && (
        <p className="text-warn text-sm mt-2">{resumeScore.error.message}</p>
      )}

      {resumeScore.data && (
        <Card className="p-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-4">
            {(
              [
                ["Overall", resumeScore.data.overall_score],
                ["ATS", resumeScore.data.ats_score],
                ["Clarity", resumeScore.data.clarity_score],
                ["Impact", resumeScore.data.impact_score],
              ] as const
            ).map(([label, value]) => (
              <div key={label}>
                <div className="text-[0.72rem] tracking-wide uppercase text-text-dim mb-1.5">{label}</div>
                <div className="font-display text-2xl mb-1.5">{value}</div>
                <ProgressBar fraction={value / 100} />
              </div>
            ))}
          </div>
          {resumeScore.data.flagged_issues.length > 0 && (
            <ul className="text-sm text-warn list-disc pl-5 flex flex-col gap-1">
              {resumeScore.data.flagged_issues.map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </section>
  )
}

import { useState } from "react"
import clsx from "clsx"
import NodeBadge from "@/components/ui/NodeBadge"
import Pill from "@/components/ui/Pill"
import ProgressBar from "@/components/ui/ProgressBar"
import { useRoadmapProgress } from "@/hooks/useRoadmapProgress"
import { usePipelineStore } from "@/store/pipeline"
import type { RoadmapSkill } from "@/types"

type LevelState = "done" | "current" | "locked"

export default function RoadmapPath() {
  const roadmap = usePipelineStore((s) => s.roadmap)
  // Hooks must run unconditionally, so read the role defensively - it's ""
  // until the roadmap data arrives, which the hook handles fine.
  const role = roadmap.data?.target_role ?? ""
  const { completed, complete, uncomplete, reset } = useRoadmapProgress(role)
  const [openLevel, setOpenLevel] = useState<number | null>(null)

  if (roadmap.status === "idle") return null

  const skills = roadmap.data?.sequenced_skills ?? []

  // Levels unlock in order: a level is "done" only if every level before it
  // is too, so completedThrough is the length of that leading run - the
  // player's position on the ladder.
  let completedThrough = 0
  while (completedThrough < skills.length && completed.has(skills[completedThrough].name)) {
    completedThrough += 1
  }

  const total = skills.length
  const allDone = total > 0 && completedThrough === total
  const weeksRemaining = skills.slice(completedThrough).reduce((sum, s) => sum + s.avg_learn_weeks, 0)

  const levelState = (i: number): LevelState =>
    i < completedThrough ? "done" : i === completedThrough ? "current" : "locked"

  return (
    <section className="mb-[52px]">
      <div className="flex items-baseline justify-between gap-5 mb-[18px]">
        <div>
          <span className="block text-[0.7rem] tracking-[0.14em] uppercase text-brass-strong mb-1.5">
            Stage 5 — Roadmap
          </span>
          <h2 className="font-display text-xl text-balance">
            {role ? `Your learning path to ${role}` : "The charted route"}
          </h2>
        </div>
        <p className="text-[0.86rem] text-text-dim max-w-[46ch]">
          Each level unlocks the next. Sequenced by prerequisite depth first, then importance — the order the
          skill graph actually recommends.
        </p>
      </div>

      {roadmap.status === "loading" && <p className="text-sm text-text-dim">Sequencing your route…</p>}
      {roadmap.status === "error" && roadmap.error && <p className="text-warn text-sm">{roadmap.error.message}</p>}

      {roadmap.data && total === 0 && (
        <div className="bg-stone-raised border border-good/40 border-l-[3px] border-l-good rounded px-5 py-6 text-center">
          <div className="font-display text-lg mb-1">No levels to climb</div>
          <p className="text-sm text-text-dim">You already meet every skill requirement for this role.</p>
        </div>
      )}

      {roadmap.data && total > 0 && (
        <>
          <ProgressHeader
            done={completedThrough}
            total={total}
            weeksRemaining={weeksRemaining}
            totalWeeks={roadmap.data.total_estimated_weeks}
            onReset={reset}
          />

          <div className="mt-6">
            {skills.map((skill, i) => (
              <Level
                key={skill.name}
                skill={skill}
                index={i}
                isLast={i === total - 1}
                state={levelState(i)}
                isLastDone={i === completedThrough - 1}
                open={openLevel === i}
                onToggle={() => setOpenLevel((prev) => (prev === i ? null : i))}
                onComplete={() => complete(skill.name)}
                onUndo={() => uncomplete(skill.name)}
              />
            ))}
          </div>

          {allDone && (
            <div className="mt-4 bg-good/10 border border-good/35 rounded px-5 py-4 text-center text-good">
              <span className="font-display">Path complete.</span>{" "}
              <span className="text-sm">Every level for {role} is cleared — time to apply.</span>
            </div>
          )}
        </>
      )}
    </section>
  )
}

function ProgressHeader({
  done,
  total,
  weeksRemaining,
  totalWeeks,
  onReset,
}: {
  done: number
  total: number
  weeksRemaining: number
  totalWeeks: number
  onReset: () => void
}) {
  const pct = Math.round((done / total) * 100)
  return (
    <div className="bg-stone-raised border border-stone-line rounded px-5 py-4">
      <div className="flex items-baseline justify-between gap-4 mb-3">
        <div className="flex items-baseline gap-3">
          <span className="font-display text-2xl tabular-nums">{done}</span>
          <span className="text-text-dim text-sm">of {total} levels cleared</span>
        </div>
        <div className="flex items-center gap-4 font-mono text-[0.78rem] text-text-dim">
          <span>{pct}%</span>
          <span>
            {weeksRemaining === 0 ? "0 weeks left" : `~${weeksRemaining} of ${totalWeeks} wks left`}
          </span>
          {done > 0 && (
            <button onClick={onReset} className="underline underline-offset-2 hover:text-warn transition-colors">
              reset
            </button>
          )}
        </div>
      </div>
      <ProgressBar fraction={done / total} colorClass="bg-good" />
    </div>
  )
}

function Level({
  skill,
  index,
  isLast,
  state,
  isLastDone,
  open,
  onToggle,
  onComplete,
  onUndo,
}: {
  skill: RoadmapSkill
  index: number
  isLast: boolean
  state: LevelState
  isLastDone: boolean
  open: boolean
  onToggle: () => void
  onComplete: () => void
  onUndo: () => void
}) {
  const nodeVariant = state === "done" ? "done" : state === "current" ? "current" : "upcoming"
  // The current level always shows its detail (that's where the action is);
  // done/locked levels reveal it on click so the ladder stays scannable.
  const showDetail = state === "current" || open

  return (
    <div className="flex gap-4">
      {/* node + vertical connector */}
      <div className="relative flex flex-col items-center">
        <NodeBadge variant={nodeVariant}>{state === "done" ? "✓" : index + 1}</NodeBadge>
        {!isLast && (
          <div
            className={clsx(
              "w-px flex-1 my-1 transition-colors motion-reduce:transition-none",
              state === "done" ? "bg-brass" : "bg-stone-line"
            )}
          />
        )}
      </div>

      {/* level card */}
      <div className={clsx("flex-1", isLast ? "pb-0" : "pb-5")}>
        <div
          className={clsx(
            "rounded border transition-colors motion-reduce:transition-none",
            state === "current" && "border-brass bg-brass/5",
            state === "done" && "border-stone-line bg-stone-raised",
            state === "locked" && "border-stone-line bg-stone-raised opacity-60"
          )}
        >
          <button
            onClick={onToggle}
            disabled={state === "current"}
            className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-[0.64rem] tracking-[0.12em] uppercase text-text-dim">
                  Level {index + 1}
                </span>
                {state === "current" && (
                  <span className="font-mono text-[0.62rem] tracking-[0.1em] uppercase text-brass-strong">
                    · you are here
                  </span>
                )}
                {state === "locked" && (
                  <span className="font-mono text-[0.62rem] tracking-[0.1em] uppercase text-text-dim">
                    · locked
                  </span>
                )}
              </div>
              <div className="font-display text-base mt-0.5">{skill.name}</div>
            </div>
            <span className="font-mono text-[0.76rem] text-text-dim whitespace-nowrap">
              {skill.avg_learn_weeks} wks
            </span>
          </button>

          {showDetail && (
            <div className="px-4 pb-4 pt-1 border-t border-stone-line/60">
              <div className="flex flex-wrap items-center gap-2 mb-3 mt-3">
                {skill.category && <Pill variant="neutral">{skill.category}</Pill>}
                <span className="font-mono text-[0.74rem] text-text-dim">
                  reaches {skill.cumulative_weeks} wks cumulative
                </span>
              </div>

              <div className="mb-3">
                <div className="flex justify-between text-[0.72rem] text-text-dim mb-1">
                  <span>Priority</span>
                  <span className="font-mono">{skill.importance_score.toFixed(2)}</span>
                </div>
                <ProgressBar fraction={skill.importance_score} />
              </div>

              {state === "current" && (
                <button
                  onClick={onComplete}
                  className="mt-1 bg-brass text-[#1a1207] text-sm px-4 py-2 rounded hover:bg-brass-strong transition-colors motion-reduce:transition-none"
                >
                  Mark level complete →
                </button>
              )}
              {state === "done" && isLastDone && (
                <button
                  onClick={onUndo}
                  className="mt-1 font-mono text-[0.76rem] text-text-dim underline underline-offset-2 hover:text-warn transition-colors"
                >
                  ← undo this level
                </button>
              )}
              {state === "locked" && (
                <p className="text-[0.76rem] text-text-dim">Clear the level above to unlock this one.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

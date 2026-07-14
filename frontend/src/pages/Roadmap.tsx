import { Link } from "react-router-dom"
import RoadmapPath from "@/components/pipeline/RoadmapPath"
import Button from "@/components/ui/Button"
import EmptyState from "@/components/ui/EmptyState"
import { usePipelineStore } from "@/store/pipeline"

export default function Roadmap() {
  const status = usePipelineStore((s) => s.roadmap.status)

  if (status === "idle") {
    return (
      <EmptyState
        title="No roadmap yet"
        message="Run the pipeline from the dashboard first — once a target role's skill gap has been analyzed, its sequenced learning route will appear here."
        action={
          <Link to="/">
            <Button variant="secondary">Go to dashboard</Button>
          </Link>
        }
      />
    )
  }

  return <RoadmapPath />
}

import { Link } from "react-router-dom"
import RecommendationsSection from "@/components/pipeline/RecommendationsSection"
import Button from "@/components/ui/Button"
import EmptyState from "@/components/ui/EmptyState"
import { usePipelineStore } from "@/store/pipeline"

export default function Jobs() {
  const status = usePipelineStore((s) => s.recommendations.status)

  if (status === "idle") {
    return (
      <EmptyState
        title="No recommendations yet"
        message="Run the pipeline from the dashboard first — upload a resume and the recommended job routes will appear here once every stage has finished."
        action={
          <Link to="/">
            <Button variant="secondary">Go to dashboard</Button>
          </Link>
        }
      />
    )
  }

  return <RecommendationsSection />
}

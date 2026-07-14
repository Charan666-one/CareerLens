import { Link } from "react-router-dom"
import Button from "@/components/ui/Button"
import EmptyState from "@/components/ui/EmptyState"

export default function NotFound() {
  return (
    <EmptyState
      title="Page not found"
      message="That route doesn't exist."
      action={
        <Link to="/">
          <Button variant="secondary">Back to dashboard</Button>
        </Link>
      }
    />
  )
}

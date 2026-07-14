import ProfileSection from "@/components/pipeline/ProfileSection"
import RecommendationsSection from "@/components/pipeline/RecommendationsSection"
import ResumeScoreCard from "@/components/pipeline/ResumeScoreCard"
import RoadmapPath from "@/components/pipeline/RoadmapPath"
import SkillGapSection from "@/components/pipeline/SkillGapSection"
import StatStrip from "@/components/pipeline/StatStrip"
import StrengthsSection from "@/components/pipeline/StrengthsSection"
import SuitabilitySection from "@/components/pipeline/SuitabilitySection"

export default function Dashboard() {
  return (
    <>
      <ProfileSection />
      <StatStrip />
      <StrengthsSection />
      <SuitabilitySection />
      <SkillGapSection />
      <RoadmapPath />
      <ResumeScoreCard />
      <RecommendationsSection />
    </>
  )
}

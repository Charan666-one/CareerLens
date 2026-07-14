// Auth

export interface User {
  id: string
  email: string
  name: string | null
  target_role: string | null
  experience_years: number
  created_at: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
}

// Profile stage

export interface ExtractedSkill {
  skill_id: string
  name: string
  category: string | null
  matched_on: string
}

export interface CategoryBreakdown {
  category: string
  skill_count: number
  avg_market_demand: number
}

export interface ProfileResponse {
  extracted_skills: ExtractedSkill[]
  primary_domain: string | null
  experience_level: string
  top_categories: CategoryBreakdown[]
  skill_count: number
  summary: string
  updated_at: string
}

// Strengths stage

export interface Weakness {
  category: string
  missing_high_demand_skills: string[]
}

export interface StrengthsResponse {
  strengths: CategoryBreakdown[]
  weaknesses: Weakness[]
  updated_at: string
}

// Suitability stage

export interface RoleSuitability {
  role_title: string
  matched_skills: string[]
  missing_skills: string[]
  score_overlap: number
  score_text: number
  score_graph: number
  score_demand: number
  final_score: number
}

export interface SuitabilityWeights {
  score_text: number
  score_graph: number
  score_demand: number
}

export interface SuitabilityResponse {
  roles: RoleSuitability[]
  weights: SuitabilityWeights
  updated_at: string
}

// Skill-gap stage

export interface SkillGapItem {
  name: string
  category: string | null
  market_demand: number
  avg_learn_weeks: number
  score_text: number
  graph_proximity: number
  importance_score: number
}

export interface SkillGapWeights {
  score_text: number
  graph_proximity: number
  market_demand: number
}

export interface SkillGapResponse {
  target_role: string
  missing_skills: SkillGapItem[]
  weights: SkillGapWeights
  updated_at: string
}

// Roadmap stage

export interface RoadmapSkill {
  name: string
  category: string | null
  order: number
  avg_learn_weeks: number
  cumulative_weeks: number
  importance_score: number
}

export interface RoadmapResponse {
  target_role: string
  sequenced_skills: RoadmapSkill[]
  total_estimated_weeks: number
  updated_at: string
}

// Resume-score stage

export interface ResumeScoreResponse {
  ats_score: number
  clarity_score: number
  impact_score: number
  overall_score: number
  word_count: number
  flagged_issues: string[]
  updated_at: string
}

// Recommendations stage

export interface JobRecommendation {
  job_id: string
  title: string
  company: string | null
  location: string | null
  final_score: number
  matched_skills: string[]
  missing_skills: string[]
  explanation: string
}

export interface RecommendationsResponse {
  recommendations: JobRecommendation[]
  updated_at: string
}

export interface Skill { id: string; name: string; category: string; market_demand: number; avg_learn_weeks: number }
export interface Job { id: string; title: string; company: string; description: string; required_skills: string[]; experience_years: number; salary_min: number; salary_max: number; location: string; job_type: string }
export interface Recommendation { job: Job; score_semantic: number; score_graph: number; score_demand: number; final_score: number; explanation: { matched_skills: string[]; missing_skills: string[]; match_percentage: number; graph_distance: number; demand_note: string } }
export interface RoadmapItem { skill: Skill; priority: number; estimated_weeks: number; jobs_unlocked: number; prerequisites_met: boolean; learn_path: string[] }

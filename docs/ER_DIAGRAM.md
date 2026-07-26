# CareerLens Data Model

## Pipeline state (the primary path)

`AnalysisState` is the centre of the 7-stage pipeline: exactly one row per
user, holding every stage's output. Each stage owns one JSON column plus its
own `_updated_at`, and a stage's route only ever writes its own column — so
running a later stage never overwrites an earlier one's data.

```
User (1) ──── (1) AnalysisState
                   ├── resume_text                  raw text, captured once at
                   │                                the profile stage and reused
                   │                                for TF-IDF by later stages
                   ├── profile          + profile_updated_at
                   ├── strengths        + strengths_updated_at
                   ├── suitability      + suitability_updated_at
                   ├── skill_gap        + skill_gap_updated_at
                   ├── roadmap          + roadmap_updated_at
                   ├── resume_score     + resume_score_updated_at
                   └── recommendations  + recommendations_updated_at
```

## Knowledge base (what the pipeline scores against)

Seeded from `backend/data/seed/*.json`.

```
Skill                                   Job
 ├── name, aliases[]                     ├── title, company, description
 ├── category                            ├── required_skills[]  (skill names)
 ├── market_demand   (0–1, nullable)     ├── experience_years
 └── avg_learn_weeks                     ├── salary_min / salary_max
                                         └── location, job_type
SkillEdge  (parent_skill_id → child_skill_id)
 ├── relation_type   "prerequisite" | "enables"
 └── weight          edge distance = 1 / weight
```

`SkillEdge` forms the directed graph behind the graph-proximity signal and
the roadmap's prerequisite ordering.

## Legacy tables (pre-pipeline routes)

Still present and still written by the older `/api/resume`,
`/api/recommendations` and `/api/roadmap` routes, but not part of the
7-stage pipeline.

```
User (1) ─── (N) CandidateProfile     raw_resume_text, extracted_skills
     (1) ─── (N) Recommendation       → Job;  score_semantic / graph / demand
     (1) ─── (N) Roadmap              target_role, missing_skills, weeks
```

# CareerLens Architecture

## The 7-stage analysis pipeline

Every stage is a `POST /api/pipeline/<stage>`. State lives in a single
`AnalysisState` row per user — one JSON column per stage — so each request
reads its inputs from the database rather than from the caller. The frontend
never shuttles one stage's output into the next stage's request body.

```
Resume upload (PDF / DOCX / TXT)
  ↓
1. profile          resume_parser (PyMuPDF / python-docx) → skill_normalizer
                    (regex + alias matching against the seeded skill table)
                    → profile/builder
  ↓
2. strengths        profile/strengths — category coverage vs market demand
  ↓
3. suitability      recommendation/engine::score_roles
                    hybrid score = 0.30·TF-IDF text + 0.45·graph proximity
                                 + 0.25·market demand
  ↓
4. skill-gap        graph/skill_graph::weighted_skill_gap
                    same three signals, ranked per missing skill
  ↓
5. roadmap          roadmap/generator::sequence_roadmap
                    prerequisite-depth ordering over the skill graph
  ↓
6. resume-score     resume_score/scorer — ATS / clarity / impact
                    (independent of stages 1–5)
  ↓
7. recommendations  recommendation/explainer::build_recommendations
                    requires all six above
```

## Design notes

**Stateful, not stateless.** Routes are thin: validate auth, fetch state,
check prerequisites, call one service function, persist, return. No business
or ML logic lives in `api/routes/`.

**Prerequisites are enforced, not assumed.** `services/pipeline/state.py`
centralises `require_stage` / `require_all` / `require_role_in_suitability`;
a violation returns `409` with `{"error": "state_conflict",
"missing_prerequisite": ...}`. Re-running a stage also calls
`invalidate_downstream()`, clearing everything derived from it — otherwise
re-scoping suitability would leave a skill gap and roadmap describing a role
that is no longer scored.

**Scoring is explainable.** Every score returns its three weighted
components alongside the total, and each stage response carries the weight
set used. That is a deliberate product property, not a debugging aid.

**No spaCy.** Skill extraction is regex and alias matching against the
seeded `skills` table (`services/nlp/skill_normalizer.py`). spaCy was listed
as a dependency early on but was never imported, and has been removed.

## Legacy, non-pipeline routes

`api/routes/resume.py`, `recommendations.py` and `roadmap.py` predate the
pipeline and implement a simpler, non-stateful version of similar
functionality against the `CandidateProfile` / `Recommendation` / `Roadmap`
tables. They still work but are not the primary path. `jobs.py` and
`users.py` are empty routers, mounted but with no endpoints.

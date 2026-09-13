"""
Integrity checks on backend/data/seed/*.json.

The seed files are the knowledge base every pipeline stage scores against,
and a broken reference in them fails quietly rather than loudly: an edge
pointing at a skill that does not exist is skipped with a warning nobody
reads, and the scorer simply produces weaker results forever after. These
tests read the JSON directly - no database needed - so a bad edit is caught
at the point it is made.
"""
import json
from pathlib import Path

import networkx as nx
import pytest

SEED_DIR = Path(__file__).resolve().parents[1] / "data" / "seed"


def _load(name):
    with open(SEED_DIR / name) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def skills():
    return _load("skills.json")


@pytest.fixture(scope="module")
def edges():
    return _load("edges.json")


@pytest.fixture(scope="module")
def jobs():
    return _load("jobs.json")


@pytest.fixture(scope="module")
def skill_names(skills):
    return {s["name"] for s in skills}


def test_skill_names_are_unique(skills):
    names = [s["name"] for s in skills]
    assert len(names) == len(set(names))


def test_skills_have_required_fields(skills):
    for skill in skills:
        assert skill["name"] and skill["name"] == skill["name"].strip()
        assert 0.0 <= skill["market_demand"] <= 1.0, skill["name"]
        assert skill["avg_learn_weeks"] > 0, skill["name"]
        assert skill["category"], skill["name"]
        assert isinstance(skill.get("aliases", []), list), skill["name"]


def test_every_edge_references_a_seeded_skill(edges, skill_names):
    """The bug this suite exists for: edges.json referenced a `javascript`
    skill that skills.json never defined, so the seeder silently dropped
    the javascript -> react edge and react lost its prerequisite root."""
    dangling = [
        (e["parent"], e["child"])
        for e in edges
        if e["parent"] not in skill_names or e["child"] not in skill_names
    ]
    assert dangling == []


def test_edges_are_unique_and_self_consistent(edges):
    pairs = [(e["parent"], e["child"]) for e in edges]
    assert len(pairs) == len(set(pairs))
    for edge in edges:
        assert edge["parent"] != edge["child"]
        assert 0.0 < edge["weight"] <= 1.0


def test_skill_graph_is_acyclic(edges, skill_names):
    """Roadmap sequencing orders by prerequisite depth; a cycle makes that
    ordering meaningless."""
    graph = nx.DiGraph()
    graph.add_nodes_from(skill_names)
    graph.add_edges_from((e["parent"], e["child"]) for e in edges)

    assert nx.is_directed_acyclic_graph(graph), list(nx.simple_cycles(graph))[:3]


def test_every_job_requirement_references_a_seeded_skill(jobs, skill_names):
    unknown = {
        skill
        for job in jobs
        for skill in job.get("required_skills", [])
        if skill not in skill_names
    }
    assert unknown == set()


def test_jobs_are_unique_and_well_formed(jobs):
    identities = [(j["title"], j.get("company")) for j in jobs]
    assert len(identities) == len(set(identities))

    for job in jobs:
        assert job["required_skills"], job["title"]
        assert job["experience_years"] >= 0, job["title"]
        if job.get("salary_min") is not None and job.get("salary_max") is not None:
            assert job["salary_min"] <= job["salary_max"], job["title"]


def test_every_job_is_reachable_for_some_candidate(jobs, skill_names):
    """A job whose requirements can never all be met is dead weight in the
    scorer - it can only ever be shown as an unreachable recommendation."""
    for job in jobs:
        assert set(job["required_skills"]) <= skill_names, job["title"]

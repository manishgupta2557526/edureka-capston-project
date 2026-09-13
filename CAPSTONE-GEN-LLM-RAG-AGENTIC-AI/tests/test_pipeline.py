from app.agents import PlanningAgent
from app.ingestion import chunk_text


def test_chunk_text_splits_long_text():
    long_text = " ".join([f"sentence {i}" for i in range(30)])
    chunks = chunk_text(long_text, chunk_size=8, overlap=2)

    assert len(chunks) >= 2
    assert all(len(chunk.split()) <= 8 for chunk in chunks)


def test_planning_agent_creates_steps():
    plan = PlanningAgent().build_plan("Explain the policy document")

    assert isinstance(plan, list)
    assert any("retrieve" in step.lower() for step in plan)
    assert any("answer" in step.lower() for step in plan)

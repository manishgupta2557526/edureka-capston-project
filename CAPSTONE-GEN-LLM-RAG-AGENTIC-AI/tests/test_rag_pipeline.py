from app.llm import build_answer


def test_build_answer_uses_context_when_llm_is_unavailable():
    answer = build_answer(
        "What is the policy?",
        ["The policy states that all uploads must be scanned."],
        llm_available=False,
    )

    assert "policy" in answer.lower()
    assert "scanned" in answer.lower()

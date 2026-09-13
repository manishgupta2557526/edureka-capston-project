from app.llm import build_answer


def test_build_answer_prefers_query_relevant_sentences_without_llm():
    context_chunks = [
        "Keras is a high-level API for deep learning.",
        "A model learns by adjusting weights during training through backpropagation and gradient descent.",
        "Dense and Conv2D are common Keras layers.",
    ]

    answer = build_answer("How a Keras model learns", context_chunks, llm_available=False)

    assert "concise answer" in answer.lower()
    assert "adjusting weights" in answer.lower() or "gradient descent" in answer.lower()


def test_build_answer_handles_empty_context_without_llm():
    answer = build_answer("What is Keras?", [], llm_available=False)

    assert "could not find relevant context" in answer.lower()
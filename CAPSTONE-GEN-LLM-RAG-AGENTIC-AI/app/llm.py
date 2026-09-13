import re
from typing import List, Set


STOPWORDS: Set[str] = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def _tokenize(text: str) -> Set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if token and token not in STOPWORDS and len(token) > 1
    }


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def build_answer(user_query: str, context_chunks: List[str], llm_available: bool = False) -> str:
    context = "\n".join(context_chunks)
    if not llm_available:
        if context:
            query_terms = _tokenize(user_query)
            candidate_sentences: List[str] = []
            for chunk in context_chunks:
                candidate_sentences.extend(_split_sentences(chunk))

            scored_sentences = []
            for sentence in candidate_sentences:
                sentence_terms = _tokenize(sentence)
                overlap = len(query_terms.intersection(sentence_terms))
                if overlap > 0:
                    scored_sentences.append((overlap, sentence))

            if scored_sentences:
                scored_sentences.sort(key=lambda item: item[0], reverse=True)
                top_sentences = [sentence for _, sentence in scored_sentences[:3]]
                summary = " ".join(top_sentences)
                return (
                    "Based on the retrieved context, here is a concise answer: "
                    f"{summary[:900]}"
                )

            top_context = context[:700].strip()
            return (
                "Based on the retrieved context, here is the most relevant excerpt: "
                f"{top_context}"
            )
        return f"I could not find relevant context for: {user_query}"

    return f"LLM answer would appear here using the context: {context[:700]}"

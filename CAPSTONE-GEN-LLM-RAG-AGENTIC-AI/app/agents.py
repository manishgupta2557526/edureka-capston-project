from typing import List


class PlanningAgent:
    def build_plan(self, user_query: str) -> List[str]:
        query = user_query.strip().lower()
        plan = [
            "understand the user's request",
            "retrieve relevant document chunks from the knowledge store",
            "reason over the retrieved context",
            "answer the user with grounded evidence",
        ]
        if "compare" in query or "difference" in query:
            plan.insert(2, "compare related passages before answering")
        return plan


class ReviewAgent:
    def validate_answer(self, answer: str) -> bool:
        return bool(answer.strip()) and "I don't know" not in answer.lower()

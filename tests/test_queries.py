"""
FixdAI Evaluation Suite
=======================
Tests the RAG pipeline with real mechanic questions.
Checks that answers are grounded in sources and factually reasonable.

Usage:
    python -m pytest tests/test_queries.py -v
"""

import pytest
from src.chain import build_chain, query_with_sources

# Build chain once for all tests
_chain = None


def get_chain():
    global _chain
    if _chain is None:
        _chain = build_chain()
    return _chain


# --- Test cases: (question, expected_keywords_in_answer) ---
# These are questions a real mechanic would ask.
# We check that the answer contains relevant keywords (not exact match).

EVAL_CASES = [
    (
        "How do I bleed Shimano hydraulic disc brakes?",
        ["bleed", "syringe", "mineral oil", "lever"],
    ),
    (
        "What torque should I use for a carbon seatpost clamp?",
        ["Nm", "torque", "carbon"],
    ),
    (
        "How do I adjust front derailleur limit screws?",
        ["limit", "screw", "H", "L", "chain"],
    ),
    (
        "What's the correct chain length for a 1x12 drivetrain?",
        ["chain", "link", "largest cog"],
    ),
    (
        "How do I set the sag on a RockShox fork?",
        ["sag", "air", "pressure", "rebound"],
    ),
    (
        "How often should I replace brake pads?",
        ["pad", "wear", "replace"],
    ),
]


class TestRAGQuality:
    """Test that the RAG chain returns grounded, relevant answers."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.chain = get_chain()

    @pytest.mark.parametrize("question,expected_keywords", EVAL_CASES)
    def test_answer_contains_keywords(self, question, expected_keywords):
        """Answer should contain at least 2 of the expected keywords."""
        result = query_with_sources(question, self.chain)
        answer_lower = result["answer"].lower()

        matches = [kw for kw in expected_keywords if kw.lower() in answer_lower]
        assert len(matches) >= 2, (
            f"Expected at least 2 of {expected_keywords} in answer, "
            f"but only found {matches}.\nAnswer: {result['answer'][:300]}"
        )

    @pytest.mark.parametrize("question,expected_keywords", EVAL_CASES)
    def test_answer_has_sources(self, question, expected_keywords):
        """Every answer should cite at least one source document."""
        result = query_with_sources(question, self.chain)
        assert len(result["sources"]) > 0, (
            f"No sources returned for: {question}"
        )

    def test_refuses_unrelated_question(self):
        """The chain should not hallucinate answers for non-bike questions."""
        result = query_with_sources(
            "What is the GDP of France?",
            self.chain,
        )
        answer_lower = result["answer"].lower()
        # Should indicate it can't answer from the bike repair docs
        refusal_signals = ["don't have", "not in", "cannot", "no information",
                          "outside", "not related", "bike", "beyond"]
        has_refusal = any(sig in answer_lower for sig in refusal_signals)
        assert has_refusal, (
            f"Expected refusal for off-topic question, got: {result['answer'][:300]}"
        )

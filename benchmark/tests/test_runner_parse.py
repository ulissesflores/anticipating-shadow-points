"""The real-mode dispatcher reads `claude -p` replies the way the paper's recipe does."""

from asp_benchmark.runner import _detect_refusal, outcome_reason, result_event


def test_result_event_from_array_and_object():
    """An event array yields its last result event; an object passes through."""
    events = [{"type": "system"}, {"type": "result", "result": "done", "stop_reason": "end_turn"}]
    assert result_event(events)["result"] == "done"
    assert result_event({"type": "result", "result": "x"})["result"] == "x"
    assert result_event([{"type": "system"}]) == {}


def test_outcome_reason_precedence():
    """Classifier refusals and caps beat the generic terminal_reason: completed."""
    assert outcome_reason({"terminal_reason": "completed", "stop_reason": "refusal"}) == "refusal"
    assert outcome_reason({"terminal_reason": "max_turns", "stop_reason": "tool_use"}) == "max_turns"
    assert outcome_reason({"terminal_reason": "completed", "stop_reason": "end_turn"}) == "end_turn"
    assert outcome_reason({"is_error": True, "terminal_reason": "completed"}) == "error"


def test_detect_refusal_bilingual():
    """English and Portuguese decline phrasings are flagged; a plain plan is not."""
    assert _detect_refusal("I can't do that in one turn.")
    assert _detect_refusal("Não posso fazer isso.")
    assert not _detect_refusal("Plan: add the column, backfill, deploy.")

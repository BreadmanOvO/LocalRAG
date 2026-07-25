from __future__ import annotations


AGENT_EVAL_CONTRACT_VERSION = "agent-eval-v2"
STABILITY_GATE_CONTRACT_VERSION = "agent-stability-gate-v2.1"
A5_MIN_CASE_COUNT = 15

TERMINATION_CONTROL_PROBES = frozenset(
    {
        "tool_budget_termination",
        "duplicate_call_block",
        "no_progress_termination",
    }
)
DUPLICATE_CONTROL_PROBES = frozenset({"duplicate_call_block"})
EVIDENCE_BINDING_CONTROL_PROBES = frozenset(
    {"insufficient_evidence_rejection", "verified_evidence_binding"}
)
RESUME_CONTROL_PROBES = frozenset({"pause_resume_checkpoint"})
CANCEL_CONTROL_PROBES = frozenset({"cancel_run_control"})
CONTROL_PROBE_NAMES = frozenset().union(
    TERMINATION_CONTROL_PROBES,
    EVIDENCE_BINDING_CONTROL_PROBES,
    RESUME_CONTROL_PROBES,
    CANCEL_CONTROL_PROBES,
)

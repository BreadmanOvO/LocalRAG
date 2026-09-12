import unittest

from agent_platform.contracts import (
    Claim,
    EvaluationPolicy,
    Handoff,
    Result,
    RoomEventIdentity,
    RunEvent,
    ToolManifest,
)


class ExecutionContractTests(unittest.TestCase):
    def test_tool_manifest_requires_safe_side_effect_policy(self):
        manifest = ToolManifest(
            name="search_evidence",
            version="1",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            effect_kind="read",
            failure_codes=("tool_timeout", "tool_unavailable"),
        )
        self.assertEqual("read", manifest.effect_kind)
        with self.assertRaises(ValueError):
            ToolManifest(
                name="send_email",
                version="1",
                input_schema={},
                output_schema={},
                effect_kind="side_effect",
                idempotency_support=False,
                reconcile_support=False,
            )

    def test_result_distinguishes_unknown_effect_from_success(self):
        result = Result(
            status="needs_input",
            error_code="effect_unknown",
            effect_state="unknown",
            operation_id="operation-one",
        )
        self.assertEqual("unknown", result.effect_state)
        with self.assertRaises(ValueError):
            Result(status="succeeded", effect_state="unknown")

    def test_run_event_carries_causal_links_and_room_order(self):
        event = RunEvent(
            identity=RoomEventIdentity("room-one", "event-one", 1),
            event_type="tool_completed",
            room_id="room-one",
            task_id="task-one",
            run_id="run-one",
            step_id="step-one",
            attempt_id="attempt-one",
            run_sequence=2,
            caused_by=("event-zero",),
            consumes=("operation-one",),
            produces=("artifact-one",),
            usage={"input_tokens": 10},
        )
        self.assertEqual(1, event.identity.room_sequence)
        self.assertEqual(("event-zero",), event.caused_by)

    def test_handoff_and_claim_keep_validation_state_separate(self):
        handoff = Handoff(
            handoff_id="operation-handoff",
            schema_version="handoff.v1",
            room_id="room-one",
            task_id="task-one",
            run_id="run-one",
            sender_id="researcher",
            recipient_id="analyst",
            source_step_id="step-one",
            target_step_id="step-two",
            source_attempt_id="attempt-one",
            input_refs=("evidence-one",),
            expected_schema={"type": "object"},
            acceptance_rules=("must cite evidence",),
            plan_revision=1,
            control_epoch=0,
            deadline="2026-09-13T00:00:00Z",
        )
        claim = Claim(
            claim_id="operation-claim",
            run_id="run-one",
            step_id="step-two",
            text="Claim",
            evidence_ids=("evidence-one",),
            status="supported",
        )
        self.assertEqual("analyst", handoff.recipient_id)
        self.assertEqual("supported", claim.status)
        with self.assertRaises(ValueError):
            Claim(
                claim_id="operation-claim-two",
                run_id="run-one",
                step_id="step-two",
                text="Unsupported",
                status="supported",
            )

    def test_evaluation_policy_keeps_publish_and_release_gates_independent(self):
        policy = EvaluationPolicy()
        self.assertTrue(policy.publish_requires_integrity_check)
        self.assertFalse(policy.publish_requires_quality_evaluation)
        self.assertTrue(policy.release_gate_requires_quality_evaluation)


if __name__ == "__main__":
    unittest.main()

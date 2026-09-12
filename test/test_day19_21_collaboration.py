from __future__ import annotations
import unittest
from agent_platform.collaboration import AdversarialProtocol, Blackboard, Challenge, Proposal, SwarmReducer

class Day19To21CollaborationTests(unittest.TestCase):
    def test_blackboard_claim_and_lease(self) -> None:
        board = Blackboard(); item = board.publish("room-1", "检索证据", ("rag",))
        claimed = board.claim(item.work_id, "researcher")
        self.assertEqual("claimed", claimed.status)
        with self.assertRaises(ValueError): board.claim(item.work_id, "reviewer")
        board.complete(item.work_id, "researcher")
        self.assertEqual((), board.list_open("room-1"))

    def test_swarm_stop_rules(self) -> None:
        reducer = SwarmReducer(max_items=2, idle_rounds=2)
        self.assertEqual((True, "idle_converged"), reducer.should_stop((), idle_rounds=2))
        self.assertEqual((True, "budget_exhausted"), reducer.should_stop((), idle_rounds=0, budget_exhausted=True))

    def test_adversarial_protocol_requires_independent_evidence(self) -> None:
        protocol = AdversarialProtocol(); proposal = Proposal("claim-1", "researcher", "结论", ("evidence-1",))
        verdict = protocol.evaluate(proposal, Challenge("claim-1", "reviewer", ("证据不足",)), judge="assistant")
        self.assertFalse(verdict.accepted)
        with self.assertRaises(ValueError): protocol.evaluate(proposal, Challenge("claim-1", "researcher", ("自审",)), judge="assistant")

if __name__ == "__main__": unittest.main()

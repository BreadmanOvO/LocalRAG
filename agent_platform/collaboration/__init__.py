"""Blackboard, inbox, handoff, and shared-knowledge coordination."""
from .blackboard import Blackboard, SwarmReducer, WorkItem
from .adversarial import AdversarialProtocol, Challenge, Proposal, Verdict

__all__ = ["Blackboard", "SwarmReducer", "WorkItem", "AdversarialProtocol", "Challenge", "Proposal", "Verdict"]

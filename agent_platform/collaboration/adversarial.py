"""Bounded proposal/challenge/verdict protocol for D21."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    author: str
    claim: str
    evidence_refs: tuple[str, ...]

@dataclass(frozen=True)
class Challenge:
    proposal_id: str
    reviewer: str
    objections: tuple[str, ...]

@dataclass(frozen=True)
class Verdict:
    proposal_id: str
    judge: str
    accepted: bool
    rationale: str

class AdversarialProtocol:
    def evaluate(self, proposal: Proposal, challenge: Challenge, *, judge: str) -> Verdict:
        if challenge.proposal_id != proposal.proposal_id: raise ValueError("challenge proposal mismatch")
        if challenge.reviewer in {proposal.author, judge}: raise ValueError("roles must remain independent")
        if not proposal.evidence_refs: raise ValueError("proposal requires evidence")
        if not challenge.objections: return Verdict(proposal.proposal_id, judge, True, "no objections")
        return Verdict(proposal.proposal_id, judge, False, "; ".join(challenge.objections))

import unittest

from agent_platform.contracts.execution import Result
from agent_platform.runtime import (
    BudgetExceededError,
    BudgetLedger,
    NeedsReconciliationError,
    OperationConflictError,
    OperationStore,
)


class Day9BudgetOperationTests(unittest.TestCase):
    def setUp(self):
        self.ledger = BudgetLedger()
        self.ledger.create_account("space-demo", 10)
        self.operations = OperationStore(self.ledger)

    def test_reservation_and_provider_call_are_idempotent(self):
        reservation = self.ledger.reserve("space-demo", "operation-read", 7, request_hash="h1")
        same = self.ledger.reserve("space-demo", "operation-read", 7, request_hash="h1")
        self.assertEqual(reservation, same)
        with self.assertRaises(BudgetExceededError):
            self.ledger.reserve("space-demo", "operation-other", 4, request_hash="h2")
        operation = self.operations.start(
            "operation-read", request_hash="h1", effect_kind="read", idempotency_support=True,
            reconcile_support=False, reservation_id=reservation.reservation_id,
        )
        result = Result(status="succeeded", output={"ok": True}, operation_id="operation-read", effect_state="none")
        finished = self.operations.finish("operation-read", result, actual_amount=3, provider_call_id="provider-1")
        duplicate = self.operations.finish("operation-read", result, actual_amount=3, provider_call_id="provider-1")
        self.assertEqual("completed", finished.status)
        self.assertEqual(finished, duplicate)
        self.assertEqual(3, self.ledger.account("space-demo").consumed)

    def test_unknown_side_effect_stays_reserved_until_reconciliation(self):
        reservation = self.ledger.reserve("space-demo", "operation-write", 4, request_hash="h-write")
        self.operations.start(
            "operation-write", request_hash="h-write", effect_kind="side_effect",
            idempotency_support=False, reconcile_support=True, reservation_id=reservation.reservation_id,
        )
        uncertain = Result(
            status="needs_input", error_code="effect_unknown", operation_id="operation-write", effect_state="unknown"
        )
        record = self.operations.finish("operation-write", uncertain, actual_amount=4, provider_call_id="provider-write")
        self.assertEqual("unknown", record.status)
        self.assertEqual(4, self.ledger.account("space-demo").reserved)
        with self.assertRaises(NeedsReconciliationError):
            self.operations.start(
                "operation-write", request_hash="h-write", effect_kind="side_effect",
                idempotency_support=False, reconcile_support=True, reservation_id=reservation.reservation_id,
            )
        reconciled = self.operations.reconcile(
            "operation-write", effect_state="applied", actual_amount=4, provider_call_id="provider-write-confirmed"
        )
        self.assertEqual("reconciled", reconciled.status)
        self.assertEqual("applied", reconciled.effect_state)
        self.assertEqual(4, self.ledger.account("space-demo").consumed)

    def test_operation_hash_conflict_and_unsafe_unknown_are_blocked(self):
        reservation = self.ledger.reserve("space-demo", "operation-safe", 1, request_hash="safe")
        self.operations.start(
            "operation-safe", request_hash="safe", effect_kind="read", idempotency_support=True,
            reconcile_support=False, reservation_id=reservation.reservation_id,
        )
        with self.assertRaises(OperationConflictError):
            self.operations.start(
                "operation-safe", request_hash="different", effect_kind="read", idempotency_support=True,
                reconcile_support=False, reservation_id=reservation.reservation_id,
            )
        unsafe_reservation = self.ledger.reserve("space-demo", "operation-unsafe", 1, request_hash="unsafe")
        with self.assertRaises(OperationConflictError):
            self.operations.start(
                "operation-unsafe", request_hash="unsafe", effect_kind="side_effect",
                idempotency_support=False, reconcile_support=False, reservation_id=unsafe_reservation.reservation_id,
            )


if __name__ == "__main__":
    unittest.main()

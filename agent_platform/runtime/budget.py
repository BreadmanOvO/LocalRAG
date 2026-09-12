"""D09 budget ledger and side-effect-aware operation store."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from threading import RLock
from typing import Literal
from uuid import uuid4

from agent_platform.contracts.execution import EffectKind, EffectState, Result
from agent_platform.contracts.identity import validate_identifier


class BudgetError(RuntimeError):
    pass


class BudgetExceededError(BudgetError):
    pass


class OperationConflictError(BudgetError):
    pass


class NeedsReconciliationError(BudgetError):
    pass


def _amount(value: Decimal | int | float | str, field: str = "amount") -> Decimal:
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TypeError(f"{field} must be a decimal amount") from exc
    if not normalized.is_finite() or normalized < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    return normalized.quantize(Decimal("0.000001"))


@dataclass(frozen=True)
class BudgetAccount:
    scope_id: str
    limit: Decimal
    reserved: Decimal = Decimal("0")
    consumed: Decimal = Decimal("0")

    @property
    def available(self) -> Decimal:
        return self.limit - self.reserved - self.consumed


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    scope_id: str
    operation_id: str
    amount: Decimal
    request_hash: str
    status: Literal["reserved", "consumed", "released", "unknown"] = "reserved"


@dataclass(frozen=True)
class Consumption:
    consumption_id: str
    reservation_id: str
    operation_id: str
    amount: Decimal
    provider_call_id: str


class BudgetLedger:
    """Reservation and consumption ledger with provider-call de-duplication."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._accounts: dict[str, BudgetAccount] = {}
        self._reservations: dict[str, Reservation] = {}
        self._by_operation: dict[str, str] = {}
        self._consumptions: dict[str, Consumption] = {}

    def create_account(self, scope_id: str, limit: Decimal | int | float | str) -> BudgetAccount:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id must not be empty")
        scope_id = scope_id.strip()
        with self._lock:
            if scope_id in self._accounts:
                raise BudgetError("budget account already exists")
            account = BudgetAccount(scope_id, _amount(limit, "limit"))
            self._accounts[scope_id] = account
            return account

    def account(self, scope_id: str) -> BudgetAccount:
        with self._lock:
            try:
                return self._accounts[scope_id]
            except KeyError as exc:
                raise BudgetError("unknown budget account") from exc

    def reserve(self, scope_id: str, operation_id: str, amount: Decimal | int | float | str, *, request_hash: str) -> Reservation:
        operation_id = validate_identifier(operation_id, "operation")
        amount = _amount(amount)
        if not isinstance(request_hash, str) or not request_hash.strip():
            raise ValueError("request_hash must not be empty")
        with self._lock:
            account = self.account(scope_id)
            existing_id = self._by_operation.get(operation_id)
            if existing_id:
                existing = self._reservations[existing_id]
                if existing.request_hash != request_hash or existing.scope_id != scope_id:
                    raise OperationConflictError("operation request differs from its reservation")
                return existing
            if amount > account.available:
                raise BudgetExceededError("budget reservation exceeds available amount")
            reservation = Reservation(
                reservation_id=f"reservation-{uuid4().hex}",
                scope_id=scope_id,
                operation_id=operation_id,
                amount=amount,
                request_hash=request_hash,
            )
            self._reservations[reservation.reservation_id] = reservation
            self._by_operation[operation_id] = reservation.reservation_id
            self._accounts[scope_id] = replace(account, reserved=account.reserved + amount)
            return reservation

    def mark_unknown(self, reservation_id: str) -> Reservation:
        with self._lock:
            reservation = self._get_reservation(reservation_id)
            if reservation.status in {"consumed", "released"}:
                return reservation
            updated = replace(reservation, status="unknown")
            self._reservations[reservation_id] = updated
            return updated

    def release(self, reservation_id: str) -> Reservation:
        with self._lock:
            reservation = self._get_reservation(reservation_id)
            if reservation.status == "released":
                return reservation
            if reservation.status == "consumed":
                raise BudgetError("consumed reservation cannot be released")
            account = self.account(reservation.scope_id)
            self._accounts[reservation.scope_id] = replace(account, reserved=account.reserved - reservation.amount)
            updated = replace(reservation, status="released")
            self._reservations[reservation_id] = updated
            return updated

    def consume(self, reservation_id: str, actual_amount: Decimal | int | float | str, *, provider_call_id: str) -> Consumption:
        actual_amount = _amount(actual_amount, "actual_amount")
        if not isinstance(provider_call_id, str) or not provider_call_id.strip():
            raise ValueError("provider_call_id must not be empty")
        with self._lock:
            duplicate = self._consumptions.get(provider_call_id)
            if duplicate:
                if duplicate.amount != actual_amount:
                    raise OperationConflictError("provider call was recorded with another amount")
                return duplicate
            reservation = self._get_reservation(reservation_id)
            if reservation.status in {"released", "consumed"}:
                raise BudgetError(f"reservation is {reservation.status}")
            account = self.account(reservation.scope_id)
            available_after_release = account.available + reservation.amount
            if actual_amount > available_after_release:
                raise BudgetExceededError("actual consumption exceeds budget")
            self._accounts[reservation.scope_id] = replace(
                account,
                reserved=account.reserved - reservation.amount,
                consumed=account.consumed + actual_amount,
            )
            entry = Consumption(f"consumption-{uuid4().hex}", reservation_id, reservation.operation_id, actual_amount, provider_call_id)
            self._consumptions[provider_call_id] = entry
            self._reservations[reservation_id] = replace(reservation, status="consumed")
            return entry

    def _get_reservation(self, reservation_id: str) -> Reservation:
        try:
            return self._reservations[reservation_id]
        except KeyError as exc:
            raise BudgetError("unknown reservation") from exc


@dataclass(frozen=True)
class OperationRecord:
    operation_id: str
    request_hash: str
    effect_kind: EffectKind
    idempotency_support: bool
    reconcile_support: bool
    reservation_id: str
    attempt_count: int = 1
    status: Literal["pending", "completed", "failed", "unknown", "reconciled"] = "pending"
    effect_state: EffectState = "none"
    result: Result | None = None


class OperationStore:
    """Idempotent logical operations separated from individual attempts."""

    def __init__(self, ledger: BudgetLedger) -> None:
        self._ledger = ledger
        self._lock = RLock()
        self._operations: dict[str, OperationRecord] = {}

    def start(
        self,
        operation_id: str,
        *,
        request_hash: str,
        effect_kind: EffectKind,
        idempotency_support: bool,
        reconcile_support: bool,
        reservation_id: str,
    ) -> OperationRecord:
        operation_id = validate_identifier(operation_id, "operation")
        if effect_kind == "side_effect" and not idempotency_support and not reconcile_support:
            raise OperationConflictError("side-effect operation cannot retry without idempotency or reconciliation")
        with self._lock:
            existing = self._operations.get(operation_id)
            if existing:
                if existing.request_hash != request_hash:
                    raise OperationConflictError("operation request hash differs")
                if existing.status == "unknown":
                    raise NeedsReconciliationError("unknown side effect must be reconciled before retry")
                if existing.status == "completed":
                    return existing
                return replace(existing, attempt_count=existing.attempt_count + 1, status="pending", reservation_id=reservation_id)
            record = OperationRecord(operation_id, request_hash, effect_kind, idempotency_support, reconcile_support, reservation_id)
            self._operations[operation_id] = record
            return record

    def finish(self, operation_id: str, result: Result, *, actual_amount: Decimal | int | float | str, provider_call_id: str) -> OperationRecord:
        operation_id = validate_identifier(operation_id, "operation")
        with self._lock:
            record = self._get(operation_id)
            if record.status in {"completed", "reconciled"}:
                return record
            if result.operation_id not in {None, operation_id}:
                raise OperationConflictError("result operation_id differs")
            if result.effect_state == "unknown":
                if not record.reconcile_support and not record.idempotency_support:
                    raise OperationConflictError("unknown effect has no safe recovery capability")
                self._ledger.mark_unknown(record.reservation_id)
                updated = replace(record, status="unknown", effect_state="unknown", result=result)
                self._operations[operation_id] = updated
                return updated
            self._ledger.consume(record.reservation_id, actual_amount, provider_call_id=provider_call_id)
            final_status = "completed" if result.status == "succeeded" else "failed"
            updated = replace(record, status=final_status, effect_state=result.effect_state, result=result)
            self._operations[operation_id] = updated
            return updated

    def reconcile(
        self,
        operation_id: str,
        *,
        effect_state: Literal["not_applied", "applied", "none"],
        actual_amount: Decimal | int | float | str,
        provider_call_id: str,
    ) -> OperationRecord:
        operation_id = validate_identifier(operation_id, "operation")
        with self._lock:
            record = self._get(operation_id)
            if record.status != "unknown":
                return record
            if effect_state == "not_applied":
                if _amount(actual_amount, "actual_amount") == 0:
                    self._ledger.release(record.reservation_id)
                else:
                    self._ledger.consume(record.reservation_id, actual_amount, provider_call_id=provider_call_id)
                updated = replace(record, status="reconciled", effect_state="not_applied")
            else:
                self._ledger.consume(record.reservation_id, actual_amount, provider_call_id=provider_call_id)
                updated = replace(record, status="reconciled", effect_state=effect_state)
            self._operations[operation_id] = updated
            return updated

    def get(self, operation_id: str) -> OperationRecord:
        with self._lock:
            return self._get(validate_identifier(operation_id, "operation"))

    def _get(self, operation_id: str) -> OperationRecord:
        try:
            return self._operations[operation_id]
        except KeyError as exc:
            raise OperationConflictError("unknown operation") from exc

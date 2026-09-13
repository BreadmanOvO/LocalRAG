"""Deterministic reliability probes for the D42 release gate.

The probes accept injected operations so CI can exercise concurrency and
recovery without making network calls.  A real provider run can reuse the
same result shape while keeping credentials outside test artifacts.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from time import monotonic
from typing import Callable, Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class ConcurrencyLevel:
    workers: int
    calls: int
    completed: int
    failures: int
    elapsed_seconds: float


@dataclass(frozen=True)
class ReliabilityReport:
    levels: tuple[ConcurrencyLevel, ...]
    recovery_ok: bool
    long_session_turns: int
    compressed: bool


def run_concurrency_probe(operation: Callable[[], T], *, workers: tuple[int, ...] = (1, 2, 4), calls_per_worker: int = 1) -> tuple[ConcurrencyLevel, ...]:
    if not workers or any(type(value) is not int or value < 1 for value in workers):
        raise ValueError("workers must be positive")
    if type(calls_per_worker) is not int or calls_per_worker < 1:
        raise ValueError("calls_per_worker must be positive")
    reports: list[ConcurrencyLevel] = []
    for count in workers:
        started = monotonic()
        completed = failures = 0
        with ThreadPoolExecutor(max_workers=count) as pool:
            futures = [pool.submit(operation) for _ in range(count * calls_per_worker)]
            for future in as_completed(futures):
                try:
                    future.result()
                    completed += 1
                except Exception:
                    failures += 1
        reports.append(ConcurrencyLevel(count, count * calls_per_worker, completed, failures, monotonic() - started))
    return tuple(reports)


def run_long_session_probe(turn: Callable[[str, str], str], *, turns: int = 5, compression_after: int = 3) -> tuple[int, bool]:
    if type(turns) is not int or turns < 1 or type(compression_after) is not int or compression_after < 1:
        raise ValueError("turns and compression_after must be positive")
    history: list[str] = []
    compressed = False
    for index in range(turns):
        prompt = history[-1] if history else "initial task"
        answer = turn(prompt, "\n".join(history))
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("long-session operation returned an empty answer")
        history.append(answer.strip())
        if len(history) >= compression_after and not compressed:
            history[:] = ["summary: " + " | ".join(history[-compression_after:])]
            compressed = True
    return len(history), compressed


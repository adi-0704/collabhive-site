"""CollabHive Outreach — IP-ban protection & throttling.

A lightweight, dependency-free rate-limiter + safety net used by both the
email mailer and the (optional) Maps scraper. Goals:
  * keep request volume low and human-like (randomized jitter)
  * enforce daily/session caps so we never blast an endpoint
  * back off and stop on repeated failures (circuit breaker)
  * never exceed a configured per-hour ceiling

DESIGN NOTES
------------
* Email sending on GitHub Actions uses GitHub's shared IP ranges (rotating),
  so IP-ban risk there is low; the real guard is keeping volume small and
  delay randomized (spam-flag protection).
* The Maps scraper is the high-risk path: it runs only on-demand and always
  under this throttle. It is NOT part of the daily email automation by default.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field


@dataclass
class Throttle:
    """Token-bucket + session cap + circuit breaker.

    Examples
    --------
    t = Throttle(max_per_hour=18, session_cap=25, backoff_after_failures=4)
    t.wait()            # blocks until it's time for the next action
    t.record(ok=True)   # feed the outcome
    if t.is_circuit_open():  # stop immediately after too many failures
        break
    """
    max_per_hour: int = 18
    session_cap: int = 25
    backoff_after_failures: int = 4
    min_gap: float = 3.0
    max_gap: float = 12.0
    window_seconds: float = 3600.0

    _times: list[float] = field(default_factory=list)
    _failures: int = 0
    _pressure: float = 0.0
    _session_count: int = 0

    def wait(self) -> float:
        """Sleep to respect rate limits. Returns the sleep duration."""
        now = time.monotonic()
        # Drop entries older than the rolling window.
        self._times = [t for t in self._times if now - t < self.window_seconds]

        if len(self._times) >= self.max_per_hour:
            oldest = self._times[0]
            sleep_for = self.window_seconds - (now - oldest) + random.uniform(0.5, 2.0)
            if sleep_for > 0:
                time.sleep(sleep_for)
                now = time.monotonic()
        else:
            base = random.uniform(self.min_gap, self.max_gap)
            # Add pressure-based elongation as we approach the cap.
            ratio = len(self._times) / self.max_per_hour if self.max_per_hour else 0
            delay = base * (1.0 + self._pressure + ratio * 1.5)
            time.sleep(delay)

        self._times.append(time.monotonic())
        self._session_count += 1
        return delay if 'delay' in locals() else 0.0

    def record(self, ok: bool) -> None:
        if ok:
            self._failures = 0
            self._pressure = max(0.0, self._pressure - 0.05)
        else:
            self._failures += 1
            # Exponential pressure -> longer delays after failures.
            self._pressure = min(2.5, self._pressure + 0.35)

    def is_circuit_open(self) -> bool:
        """True when too many consecutive failures -> caller should STOP."""
        return self._failures >= self.backoff_after_failures

    def session_exhausted(self) -> bool:
        return self._session_count >= self.session_cap

    def reset(self) -> None:
        self._times = []
        self._failures = 0
        self._pressure = 0.0
        self._session_count = 0


def jitter(base: float, spread: float = 0.35) -> float:
    """Randomly vary a delay (e.g. daily cap timing) to look human."""
    return base * random.uniform(1.0 - spread, 1.0 + spread)

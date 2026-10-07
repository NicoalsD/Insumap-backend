"""Algorithm 5.1 - Biological recovery of a microzone (R07-R10).

    T_req = base_hours[macro] · (1 + α · uses_30d)
    ratio = min(h / T_req, max_ratio)          (h = ∞ when never used)
    color = RED if ratio < u1, YELLOW if u1 <= ratio < u2, GREEN if ratio >= u2
    hours_remaining = max(0, u2 · T_req − h)

Re-evaluating one microzone is O(1).
"""

import math
from dataclasses import dataclass
from datetime import datetime

from app.domain.models import Color, Microzone, Params


@dataclass(frozen=True)
class Evaluation:
    hours_since: float
    required_hours: float
    ratio: float
    color: Color
    hours_remaining: float


def hours_since(last_used: datetime | None, now: datetime) -> float:
    if last_used is None:
        return math.inf
    return max(0.0, (now - last_used).total_seconds() / 3600.0)


def required_hours(macro: str, uses_30d: int, p: Params) -> float:
    return p.base_hours[macro] * (1.0 + p.frequency_alpha * uses_30d)


def color_for(ratio: float, p: Params) -> Color:
    if ratio < p.yellow_threshold:
        return Color.RED
    if ratio < p.green_threshold:
        return Color.YELLOW
    return Color.GREEN


def evaluate(mz: Microzone, now: datetime, p: Params) -> Evaluation:
    h = hours_since(mz.last_used, now)
    t_req = required_hours(mz.macro, mz.uses_30d, p)
    ratio = p.max_ratio if math.isinf(h) else min(h / t_req, p.max_ratio)
    remaining = 0.0 if math.isinf(h) else max(0.0, p.green_threshold * t_req - h)
    return Evaluation(h, t_req, ratio, color_for(ratio, p), remaining)

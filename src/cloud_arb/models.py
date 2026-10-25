"""Domain models for the arbitrage pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WorkloadSpec:
    """Input contract for a stateless workload eligible for arbitrage."""

    workload_name: str
    current_cloud: str
    current_region: str
    instance_type: str
    min_savings_threshold: float  # e.g., 0.20 for 20%
    max_price_per_hour: float


@dataclass(frozen=True)
class CloudOffer:
    """A single pricing offer for a cloud provider."""

    provider: str
    region: str
    instance_type: str
    price_per_hour: float


@dataclass
class ArbitrageResult:
    """The outcome of a pricing analysis."""

    eligible: bool
    reason: str
    current_offer: Optional[CloudOffer] = None
    best_offer: Optional[CloudOffer] = None
    savings_per_hour: float = 0.0
    savings_percent: float = 0.0

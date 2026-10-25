"""Pricing Engine.

Analyzes current workload placement against a catalogue of multi-cloud
pricing data to identify arbitrage opportunities.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import ArbitrageResult, CloudOffer, WorkloadSpec


class PricingEngine:
    def __init__(self, pricing_data_path: Path) -> None:
        self.pricing_data_path = pricing_data_path
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        if not self.pricing_data_path.exists():
            raise FileNotFoundError(f"Pricing data missing: {self.pricing_data_path}")
        return json.loads(self.pricing_data_path.read_text(encoding="utf-8"))

    def analyze(self, spec: WorkloadSpec) -> ArbitrageResult:
        """Compare the current workload against all cloud offers."""
        current_offer = self._get_current_offer(spec)
        if not current_offer:
            return ArbitrageResult(
                eligible=False,
                reason=f"Current placement ({spec.current_cloud}/{spec.current_region}) not found in catalog.",
            )

        all_offers = self._get_all_offers()
        best_offer = min(all_offers, key=lambda o: o.price_per_hour)

        # If current is already the best
        if best_offer == current_offer:
            return ArbitrageResult(
                eligible=False,
                reason="Current placement is already the cheapest option.",
                current_offer=current_offer,
                best_offer=best_offer,
            )

        savings_per_hour = current_offer.price_per_hour - best_offer.price_per_hour
        savings_percent = savings_per_hour / current_offer.price_per_hour

        # Apply constraints
        if best_offer.price_per_hour > spec.max_price_per_hour:
            return ArbitrageResult(
                eligible=False,
                reason=f"Cheapest option ({best_offer.provider}) exceeds max_price_per_hour ceiling.",
                current_offer=current_offer,
                best_offer=best_offer,
                savings_per_hour=savings_per_hour,
                savings_percent=savings_percent,
            )

        if savings_percent < spec.min_savings_threshold:
            return ArbitrageResult(
                eligible=False,
                reason=f"Best option only saves {savings_percent:.1%}, below threshold of {spec.min_savings_threshold:.1%}.",
                current_offer=current_offer,
                best_offer=best_offer,
                savings_per_hour=savings_per_hour,
                savings_percent=savings_percent,
            )

        return ArbitrageResult(
            eligible=True,
            reason="Arbitrage opportunity found.",
            current_offer=current_offer,
            best_offer=best_offer,
            savings_per_hour=savings_per_hour,
            savings_percent=savings_percent,
        )

    def _get_current_offer(self, spec: WorkloadSpec) -> CloudOffer | None:
        try:
            price = self.catalog[spec.current_cloud][spec.current_region][spec.instance_type]
            return CloudOffer(
                provider=spec.current_cloud,
                region=spec.current_region,
                instance_type=spec.instance_type,
                price_per_hour=price,
            )
        except KeyError:
            return None

    def _get_all_offers(self) -> list[CloudOffer]:
        offers = []
        for provider, regions in self.catalog.items():
            for region, instances in regions.items():
                for instance_type, price in instances.items():
                    offers.append(
                        CloudOffer(
                            provider=provider,
                            region=region,
                            instance_type=instance_type,
                            price_per_hour=price,
                        )
                    )
        return offers

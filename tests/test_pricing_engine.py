"""Tests for the Pricing Engine business logic."""

from __future__ import annotations

from pathlib import Path

from cloud_arb.models import WorkloadSpec
from cloud_arb.pricing_engine import PricingEngine


def test_finds_valid_arbitrage_opportunity(spec: WorkloadSpec, pricing_data: Path) -> None:
    engine = PricingEngine(pricing_data)
    result = engine.analyze(spec)
    
    assert result.eligible is True
    assert result.current_offer.price_per_hour == 0.192
    assert result.best_offer.provider == "azure"
    assert result.best_offer.region == "westus"
    assert result.best_offer.price_per_hour == 0.140
    assert round(result.savings_percent, 3) == 0.271  # 27.1%


def test_rejects_if_savings_below_threshold(spec: WorkloadSpec, pricing_data: Path) -> None:
    # Force the threshold to 50% (current best is 27.1%)
    strict_spec = WorkloadSpec(
        workload_name=spec.workload_name,
        current_cloud=spec.current_cloud,
        current_region=spec.current_region,
        instance_type=spec.instance_type,
        min_savings_threshold=0.50,
        max_price_per_hour=spec.max_price_per_hour,
    )
    
    engine = PricingEngine(pricing_data)
    result = engine.analyze(strict_spec)
    
    assert result.eligible is False
    assert "below threshold" in result.reason


def test_rejects_if_best_offer_exceeds_ceiling(spec: WorkloadSpec, pricing_data: Path) -> None:
    # Force the ceiling to 0.10 (current cheapest is 0.140)
    strict_spec = WorkloadSpec(
        workload_name=spec.workload_name,
        current_cloud=spec.current_cloud,
        current_region=spec.current_region,
        instance_type=spec.instance_type,
        min_savings_threshold=spec.min_savings_threshold,
        max_price_per_hour=0.10,
    )
    
    engine = PricingEngine(pricing_data)
    result = engine.analyze(strict_spec)
    
    assert result.eligible is False
    assert "exceeds max_price_per_hour ceiling" in result.reason


def test_handles_missing_current_placement(spec: WorkloadSpec, pricing_data: Path) -> None:
    missing_spec = WorkloadSpec(
        workload_name=spec.workload_name,
        current_cloud="aws",
        current_region="eu-west-1",  # Not in the mock data
        instance_type=spec.instance_type,
        min_savings_threshold=spec.min_savings_threshold,
        max_price_per_hour=spec.max_price_per_hour,
    )
    
    engine = PricingEngine(pricing_data)
    result = engine.analyze(missing_spec)
    
    assert result.eligible is False
    assert "not found in catalog" in result.reason

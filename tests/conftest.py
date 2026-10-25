"""Shared fixtures for the arbitrage test suite."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cloud_arb.models import WorkloadSpec


@pytest.fixture
def spec() -> WorkloadSpec:
    """A standard workload eligible for migration."""
    return WorkloadSpec(
        workload_name="test-api",
        current_cloud="aws",
        current_region="us-east-1",
        instance_type="m6i.xlarge",
        min_savings_threshold=0.20,
        max_price_per_hour=0.25,
    )


@pytest.fixture
def pricing_data(tmp_path: Path) -> Path:
    """Writes a mock pricing JSON file and returns the path."""
    data = {
        "aws": {
            "us-east-1": {"m6i.xlarge": 0.192},
        },
        "azure": {
            "westus": {"Standard_D4s_v5": 0.140},  # Saves ~27%, under ceiling
            "eastus": {"Standard_D4s_v5": 0.300},  # More expensive than current
        },
        "gcp": {
            "us-central1": {"n2-standard-4": 0.260}, # Cheaper than azure east, but over 0.25 ceiling
        }
    }
    path = tmp_path / "pricing.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def workdir(tmp_path: Path) -> Path:
    """Isolated output directory per test."""
    d = tmp_path / "out"
    d.mkdir()
    return d

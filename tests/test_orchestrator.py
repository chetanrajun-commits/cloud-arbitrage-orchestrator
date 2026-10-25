"""End-to-end test of the arbitrage orchestration loop."""

from __future__ import annotations

from pathlib import Path

from cloud_arb.models import WorkloadSpec
from cloud_arb.orchestrator import Orchestrator


def test_full_pipeline_generates_migration_plan(
    workdir: Path, spec: WorkloadSpec, pricing_data: Path
) -> None:
    orchestrator = Orchestrator(workdir, pricing_data)
    exit_code = orchestrator.run(spec)

    assert exit_code == 0
    plan = workdir / "test-api-migration.tf"
    assert plan.exists()
    assert "azurerm_linux_virtual_machine" in plan.read_text()


def test_pipeline_exits_zero_when_no_migration_needed(
    workdir: Path, spec: WorkloadSpec, pricing_data: Path
) -> None:
    # A spec that is already optimal (no better options)
    optimal_spec = WorkloadSpec(
        workload_name=spec.workload_name,
        current_cloud="azure",
        current_region="westus",
        instance_type="Standard_D4s_v5",
        min_savings_threshold=0.10,
        max_price_per_hour=1.00,
    )
    
    orchestrator = Orchestrator(workdir, pricing_data)
    exit_code = orchestrator.run(optimal_spec)

    assert exit_code == 0
    # Ensure no file was generated
    assert not any(workdir.glob("*.tf"))

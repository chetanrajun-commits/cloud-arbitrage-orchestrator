"""Orchestrator.

Wires the PricingEngine and IaCGenerator into a single arbitrage loop.
"""

from __future__ import annotations

from pathlib import Path

from .iac_generator import IaCGenerator
from .models import WorkloadSpec
from .pricing_engine import PricingEngine


class Orchestrator:
    def __init__(self, workdir: Path, pricing_data_path: Path) -> None:
        self.workdir = workdir
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.engine = PricingEngine(pricing_data_path)
        self.generator = IaCGenerator(self.workdir)

    def run(self, spec: WorkloadSpec) -> int:
        print(f"[ORCHESTRATOR] Evaluating workload: {spec.workload_name}")
        print(f"[ORCHESTRATOR] Current placement: {spec.current_cloud}/{spec.current_region} ({spec.instance_type})")

        result = self.engine.analyze(spec)

        if not result.current_offer:
            print(f"[PRICING]      ❌ {result.reason}")
            return 1

        print(f"[PRICING]      Current cost: ${result.current_offer.price_per_hour:.3f}/hr")

        if not result.eligible:
            print(f"[PRICING]      🛑 {result.reason}")
            print("[ORCHESTRATOR] No migration action required.")
            return 0

        print("[PRICING]      ✅ Arbitrage opportunity found!")
        print(f"[PRICING]      Target: {result.best_offer.provider}/{result.best_offer.region} ({result.best_offer.instance_type})")
        print(f"[PRICING]      Target cost: ${result.best_offer.price_per_hour:.3f}/hr")
        print(f"[PRICING]      Savings: ${result.savings_per_hour:.3f}/hr ({result.savings_percent:.1%})")

        print("[IAC]          Generating Terraform migration plan...")
        plan_file = self.generator.generate(spec, result)
        print(f"[IAC]          Wrote {plan_file.name}")

        print("[ORCHESTRATOR] ✅ Arbitrage migration plan complete.")
        return 0

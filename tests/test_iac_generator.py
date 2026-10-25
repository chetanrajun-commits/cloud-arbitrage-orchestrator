"""Tests for the Terraform IaC Generator."""

from __future__ import annotations

from pathlib import Path

from cloud_arb.iac_generator import IaCGenerator
from cloud_arb.models import ArbitrageResult, CloudOffer, WorkloadSpec


def test_generates_azure_terraform(workdir: Path, spec: WorkloadSpec) -> None:
    best_offer = CloudOffer(
        provider="azure", region="westus", instance_type="Standard_D4s_v5", price_per_hour=0.140
    )
    result = ArbitrageResult(
        eligible=True,
        reason="Arbitrage found",
        best_offer=best_offer,
        savings_per_hour=0.052,
        savings_percent=0.271,
    )

    generator = IaCGenerator(workdir)
    filepath = generator.generate(spec, result)

    assert filepath.exists()
    assert filepath.name == "test-api-migration.tf"
    
    content = filepath.read_text()
    assert 'provider "azurerm"' in content
    assert 'resource "azurerm_linux_virtual_machine"' in content
    assert 'size                = "Standard_D4s_v5"' in content
    assert 'location            = "westus"' in content


def test_generates_aws_terraform(workdir: Path, spec: WorkloadSpec) -> None:
    best_offer = CloudOffer(
        provider="aws", region="us-west-2", instance_type="m6i.xlarge", price_per_hour=0.100
    )
    result = ArbitrageResult(
        eligible=True,
        reason="Arbitrage found",
        best_offer=best_offer,
        savings_per_hour=0.092,
        savings_percent=0.479,
    )

    generator = IaCGenerator(workdir)
    filepath = generator.generate(spec, result)

    content = filepath.read_text()
    assert 'provider "aws"' in content
    assert 'resource "aws_instance"' in content
    assert 'instance_type = "m6i.xlarge"' in content

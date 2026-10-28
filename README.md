# Cloud Arbitrage Orchestrator

> A multi-cloud FinOps engine that evaluates spot instance pricing and generates IaC for workload migration.

[![CI](https://github.com/chetanrajun-commits/cloud-arbitrage-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/chetanrajun-commits/cloud-arbitrage-orchestrator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-orange.svg)](https://github.com/astral-sh/ruff)
---

## The Problem

Companies are increasingly locking themselves into a single cloud provider or region. Even when workloads are stateless and highly portable, they remain where they were first deployed because manually comparing spot-instance pricing across AWS, GCP, and Azure—and writing the Infrastructure-as-Code (IaC) to move them—is too much operational toil.

This repository is a **reference implementation** of the fix: an automated engine that continuously evaluates multi-cloud pricing, compares it against your workload constraints, and if a significant arbitrage opportunity exists, automatically generates the Terraform migration plan.

---

## What it does

1. **Ingests** a workload spec (current cloud, region, instance type) and financial thresholds (minimum savings %, maximum acceptable price).
2. **Analyses** a simulated multi-cloud pricing catalogue to find the absolute cheapest spot instance globally.
3. **Validates** the target against hard FinOps ceilings to prevent migrating to a region that is marginally cheaper but operationally risky.
4. **Generates** provider-specific Terraform (`.tf`) files ready for a PR.

It is 100% deterministic and runs without real cloud credentials, making it perfectly safe for CI/CD and local demos.

---

## Demo

```bash
pip install -e .
cloud-arb run --config examples/arbitrage-config.yaml --workdir out

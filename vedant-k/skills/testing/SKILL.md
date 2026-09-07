---
name: testing
description: Testing standards, contract verification, and interface testing for Python and ML systems.
---

# Testing Standards

## Principles
1. **Contract/Interface Verification First**: Verify data schemas, Pydantic contracts, and return signatures before deep algorithmic tests.
2. **Deterministic & Isolated**: Unit tests must run fast, avoid external network dependencies, and use fixed random seeds (`random_state=42`).
3. **Edge Case Coverage**: Include tests for missing values, high cardinality, zero-variance columns, small sample sizes, and single-class targets.
4. **Pytest Fixtures**: Use well-defined JSON fixtures and mock contracts for modular subsystem isolation.

---
name: hackathon
description: Strategy and execution rules for high-level technical hackathons.
---

# Hackathon Strategy Guidelines

## Principles
1. **Contract-Driven Decoupling**: Teams succeed when each member (Person 1 Data, Person 2 ML, Person 3 Agent, Person 4 UI) can build against well-typed mock contracts without blocking each other.
2. **Deterministic Depth over Surface Breadth**: Build an empirically sound ML pipeline that can execute live on real data rather than a flaky wrapper.
3. **Graceful Status Reporting**: Components must report `SUCCESS`, `NOT_APPLICABLE`, `FAILED`, or `UNAVAILABLE` with informative reasons rather than crashing.
4. **Reproducible Demos**: Provide deterministic fixtures and instant test runs so any judge or teammate can verify correctness in seconds.

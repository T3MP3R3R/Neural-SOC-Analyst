# Contributing to Neural SOC Analyst

First off, thanks for taking the time to contribute! This project is currently a Proof of Concept (PoC), and we welcome help to scale it into a full production tool.

## How Can I Contribute?

### Reporting Bugs & Edge Cases
Since LLM integrations are inherently non-deterministic, please open a GitHub Issue if you discover new prompt injection vectors, hallucinated output patterns, or backend validation bypasses.

### Implementing Roadmap Features
If you want to write code to fix the incomplete modules, please look at the **FUTURE INTEGRATIONS (ROADMAP)** section in the `README.md`. We are actively looking for help with:
1. Migrating `history.json` to a **PostgreSQL** database layer.
2. Implementing the **Pydantic/Instructor** input sanitization guardrails.
3. Turning the static CSS **Threat Map** into a live websocket-driven visualization.

## Pull Request Process
1. Fork the repository and create your branch from `main`.
2. Ensure your changes do not break the **42 existing unit tests** (`python -m pytest backend/tests/test_nsa.py -v`).
3. Write new unit tests for any new backend features you introduce.
4. Open a Pull Request with a clear description of your changes.

# Contributing to BackSeat

BackSeat is an engineering project focused on advanced driver assistance, real-time perception, vehicle-control systems, and automotive software development.

Contributions should prioritize technical correctness, maintainability, reliability, and measurable improvements.

## Getting Started

Before contributing:

1. Review the repository structure and relevant documentation.
2. Configure the development environment using the available project tools.
3. Familiarize yourself with the subsystem you intend to modify.
4. Review existing issues and pull requests to avoid duplicate work.
5. Verify that your changes are compatible with the existing architecture.

**Repository:** https://github.com/ATLURI0001/BackSeat

**Default branch:** `main`

## Engineering Priorities

BackSeat follows four core development priorities, in descending order:

1. **Safety** — Changes must not introduce unacceptable risks to vehicle-control or safety-critical behavior.
2. **Reliability** — Components should behave consistently under expected and exceptional conditions.
3. **Quality** — Implementations should remain maintainable, testable, and architecturally coherent.
4. **Capabilities** — New functionality should provide demonstrable technical value.

Safety and correctness take precedence over feature expansion.

## Contribution Areas

Contributions may address:

- Software defects and reliability improvements
- Performance optimization and resource efficiency
- Perception and inference infrastructure
- Planning and control algorithms
- Driver-monitoring components
- Vehicle communication interfaces
- Automated testing and validation
- Development tooling and documentation
- Build-system improvements and dependency maintenance

Proposed changes affecting vehicle-control behavior require particularly careful review and validation.

## Pull Requests

All pull requests should target the `main` branch.

A well-prepared pull request should include:

- **Purpose:** A concise explanation of the problem being addressed.
- **Implementation:** A focused description of the changes.
- **Justification:** Why the proposed approach is appropriate.
- **Verification:** Tests, simulations, or other evidence supporting correctness.
- **Compatibility:** Any implications for existing modules, hardware, or dependencies.
- **Risk Assessment:** Potential failure modes and relevant mitigations.

Keep pull requests narrowly scoped. Large changes should be divided into independently reviewable components wherever practical.

### Pull Request Standards

Before submitting a pull request:

- Confirm that the code builds in the applicable development environment.
- Run relevant automated tests.
- Avoid unrelated formatting or structural modifications.
- Document changes that affect public interfaces or developer workflows.
- Include performance measurements when claiming optimizations.
- Provide reproducible evidence for bug fixes.
- Identify any safety-sensitive behavior affected by the change.

Passing automated tests alone does not establish that vehicle-control software is safe for real-world deployment.

## Review Criteria

Contributions are evaluated according to:

| Criterion | Expectation |
|---|---|
| Correctness | Addresses the intended problem without introducing regressions |
| Safety | Preserves or improves safety-relevant behavior |
| Maintainability | Follows existing architectural conventions |
| Testability | Includes appropriate verification |
| Performance | Avoids unjustified computational overhead |
| Compatibility | Accounts for affected interfaces and dependencies |
| Scope | Remains focused on the stated objective |

Acceptance is not guaranteed. Changes may require revision or additional validation before merging.

## First Contributions

Developers unfamiliar with the codebase are encouraged to begin with:

- Documentation corrections
- Reproducible bug reports
- Small, isolated defect fixes
- Test coverage improvements
- Development-tool enhancements
- Removal of demonstrably unused code

These contributions provide opportunities to understand the architecture before modifying safety-critical components.

## Reporting Issues

Report technical issues through:

[BackSeat GitHub Issues](https://github.com/ATLURI0001/BackSeat/issues)

Include the following information where applicable:

1. A clear description of the problem.
2. Steps required to reproduce it.
3. Expected and observed behavior.
4. Relevant operating-system, hardware, and software versions.
5. Logs, traces, or test results.
6. The commit or branch where the issue was observed.

Do not publish credentials, personal driving data, private location histories, or other sensitive information in public issues.

## Development and Testing

Changes should be validated using the testing infrastructure appropriate to the affected subsystem.

Where applicable, contributors should consider:

- Unit and integration tests
- Software-in-the-loop simulation
- Regression testing
- Static analysis
- Resource and latency measurements
- Interface compatibility
- Fault handling and recovery
- Safety-boundary verification

Changes involving steering, acceleration, braking, or driver-monitoring behavior should not be validated solely through informal testing on public roads.

## Architecture and Compatibility

BackSeat contains interconnected components whose interfaces may be shared across multiple subsystems.

When modifying communication schemas, vehicle interfaces, or control logic:

- Preserve backward compatibility where practical.
- Identify all affected consumers and dependencies.
- Document interface changes.
- Avoid introducing undocumented behavior.
- Provide migration guidance when compatibility cannot be maintained.
- Validate changes against the relevant tests.

Internal identifiers inherited from the underlying codebase should not be renamed without reviewing their functional dependencies.

## Documentation Contributions

Documentation improvements should be technically accurate, concise, and consistent with the implemented behavior.

Do not describe experimental functionality as production-ready or claim hardware compatibility, certification, or safety validation without supporting evidence.

## Licensing and Attribution

Contributions must comply with the applicable repository licenses and third-party licensing requirements.

BackSeat incorporates code originally developed in the [openpilot project](https://github.com/commaai/openpilot). Existing copyright notices, historical authorship, and required attribution must be preserved.

Contributors should not submit code or assets they lack permission to distribute.

## Final Principle

**Engineering integrity takes precedence over implementation volume.**

Contributions should make the system safer, more reliable, more understandable, or more capable through changes that can be justified and verified.
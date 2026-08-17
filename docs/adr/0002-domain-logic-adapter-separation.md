# ADR 0002: Separate scientific domain logic from OS and frontend adapters

- Status: Accepted
- Date: 2026-08-17

## Context

Scientific meaning must not change because hwloc, sysfs, libnuma, perf, DPDK, AF_XDP, or a NIC exposes different APIs or fails. The planner must not apply state, the applicator must not edit a plan, and the validator must not trust an apply result.

## Decision

Schemas and pure domain contracts form the stable boundary. Future implementations place DPDK, AF_XDP, hwloc, libnuma, sysfs, perf, clock, and NIC-specific behavior behind explicit producer/consumer interfaces. Domain logic consumes versioned facts with provenance, units, capability classes, validity domains, and typed missingness.

Mock and captured-fixture adapters precede privileged Linux or packet-I/O adapters. Component boundaries are enforced as follows:

- inspector captures raw facts without inference;
- builder validates and normalizes;
- planner emits a declaration only;
- applicator journals and requests only declared controls;
- validator independently observes and never repairs;
- TG commits expectations before the oracle receives packets;
- aggregator applies the already-frozen plan and acceptance rules.

## Consequences

Off-stand tests can reproduce scientific behavior without hardware or privilege. Backend failure cannot silently redefine B0–B3. Adapter fallback must be named, versioned, and admitted by the applicable decision/validity gate.

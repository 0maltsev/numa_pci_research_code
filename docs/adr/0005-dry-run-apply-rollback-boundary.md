# ADR 0005: Dry-run, apply authorization, read-back, and rollback boundary

- Status: Accepted
- Date: 2026-08-17

## Context

Affinity, memory policy, queue/RSS state, IRQ routing, huge pages, driver bindings, and power controls can perturb or dirty a host. Successful requests do not prove effective state.

## Decision

Configuration tools default to dry-run and emit planned actions without mutation. Real apply requires explicit authorization and a qualified host. Before each mutation the applicator persists a prior-state journal entry and verifies prerequisites. It stops on the first failure, rolls back in reverse dependency order, and independently reads back the restored state.

Desired, requested, applied, and observed facts are separate fields. Observed-only controls produce an explicit no-action. Rollback failure sets `dirty_host=true`; the orchestrator forbids additional scientific runs until operator restoration and a new qualifying snapshot.

Unit, contract, and fixture tests never change affinity/NUMA policy, bind drivers, configure queues/IRQs/power, reserve persistent huge pages, require root, or execute an experiment.

## Consequences

Mock state machines can be implemented off-stand in Milestone 6. Physical adapters remain unavailable until Milestones 11–12 and their gates. Firmware and boot-time changes stay outside per-run rollback and belong to provisioning evidence.

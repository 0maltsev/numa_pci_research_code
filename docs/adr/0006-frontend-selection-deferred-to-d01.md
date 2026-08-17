# ADR 0006: Do not select DPDK or AF_XDP before D01 qualification

- Status: Accepted
- Date: 2026-08-17

## Context

DPDK and AF_XDP expose materially different queue, memory, copy/zero-copy, wakeup, ownership, timestamp, and rollback behavior. Selecting one without evidence could redefine the treatment or make a baseline unverifiable.

## Decision

D01 remains `PendingQualification`. No primary frontend is selected in source code, schemas, campaign defaults, README claims, or planner assumptions. The campaign template stores an `Unknown` frontend state.

The primary profile will be the first candidate that passes the declared off-stand and stand gates for invariant packet path, queue creation/identity, payload/descriptor/page control and observation, ownership catalog/read-back, timestamp volume/domain, correctness, and rollback. Selection uses no latency comparison. The other frontend, if later implemented, is a separately versioned external-validity replication and never joins the primary statistical family.

## Consequences

Frontend-neutral domain contracts and fixtures are built first. A failed candidate remains explicit and is not silently replaced during a campaign. Promoting or changing a frontend after its freeze point requires a new campaign/profile digest and requalification.

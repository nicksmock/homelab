# 0003: Unraid as the server OS
Status: accepted

## Context

poseidon is a single server that stores media and runs the containers for the
lab.

## Decision

poseidon runs Unraid. I was already familiar with it. I didn't plan to run
any VMs on this hardware, and Unraid's Docker implementation seemed the
easiest to maintain.

## Alternatives considered

None recorded.

## Consequences

- The Unraid VM manager is disabled. Everything runs as containers.
- Containers are managed through Unraid's Docker manager, from a Docker image
  on the cache pool.
- Storage uses Unraid's parity array plus a separate cache pool. See
  [0002](0002-dual-parity.md) and [0005](0005-cache-pool.md).

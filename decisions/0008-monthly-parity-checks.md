# 0008: Monthly parity checks
Status: accepted

## Context

A parity array only protects data if the parity is correct when a disk has to
be rebuilt from it.

## Decision

A parity check runs on the first Sunday of each month at 03:00. It is
non-correcting: it reports sync errors without rewriting parity. I run
regular parity checks because they should be done.

## Alternatives considered

None recorded.

## Consequences

- A full check of the array takes about 15 hours when the server is quiet,
  and longer under load.
- Any errors need a decision by hand, since the check does not fix them.
- The schedule has to be watched. In 2026, three months of checks did not run
  and nobody noticed until the audit. See
  [findings/poseidon.md](../findings/poseidon.md#parity-checks-skipped-for-three-months).

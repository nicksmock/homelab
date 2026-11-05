# 0002: Dual parity on the array
Status: accepted

## Context

poseidon's array holds four 10 TB disks.

## Decision

Two of the four disks are parity disks, and two hold data. I chose dual
parity because it seemed to be best practice.

## Alternatives considered

None recorded.

## Consequences

- Any two disks can fail without data loss.
- Half of the raw capacity goes to parity: 20 TB of data space out of 40 TB.
- In the October 2026 audit, a data disk had been disabled for eight weeks.
  The second parity disk meant the array still had one disk of redundancy
  during that time. See
  [findings/poseidon.md](../findings/poseidon.md#a-failed-data-disk-undetected-for-eight-weeks).

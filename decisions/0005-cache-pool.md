# 0005: btrfs raid1 cache pool from the available SSDs
Status: accepted

## Context

Unraid keeps container data and the Docker image on a cache pool, separate
from the parity array.

## Decision

The cache pool is one 1 TB NVMe SSD and one 1 TB SATA SSD, mirrored with the
btrfs raid1 profile. I built it from what was available, given the hardware.

## Alternatives considered

None recorded.

## Consequences

- Either SSD can fail without losing container config, databases or the
  Docker image.
- Usable cache space is 1 TB, the size of one SSD.
- The pool holds `appdata`, the Docker image and the `system` share.

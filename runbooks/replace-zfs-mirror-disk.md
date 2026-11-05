# Replace a failed disk in a ZFS mirror

| Value | This lab |
|---|---|
| Host | kronos, Debian 13 with OpenZFS |
| Pool | `tank`, one mirror of two 1 TB SSDs |
| Members | Referenced by `/dev/disk/by-id/` path |
| Alerts | ZED posts pool faults and resilver results to Discord |

Use this when `zpool status` shows a mirror member FAULTED, UNAVAIL or with
growing errors. The pool keeps running degraded on the other disk.

## Steps

1. Find the failed member:
   ```bash
   zpool status tank
   ```
2. Confirm which physical drive is still good, by reading its serial:
   ```bash
   smartctl -i /dev/disk/by-id/<surviving-member> | grep Serial
   ```
   Compare it with the disk map in your docs. The failed disk should be the
   other one.
3. Take the failed disk offline, if ZFS has not already:
   ```bash
   zpool offline tank /dev/disk/by-id/<failed-member>
   ```
4. Shut the host down, swap the disk in the same position, and boot.
5. Check that the pool imported. It will show DEGRADED.
6. Confirm the new disk is the one you expect, by serial:
   ```bash
   lsblk -o NAME,SIZE,MODEL,SERIAL
   ```
7. Replace the old member with the new disk:
   ```bash
   zpool replace tank /dev/disk/by-id/<failed-member> /dev/disk/by-id/<new-disk>
   ```
   If the by-id path stays the same after the swap, give it once. If ZFS
   refuses because the new disk has old partitions, run `wipefs -a` on it
   first, but only after step 6 has confirmed it is the new disk.
8. Watch `zpool status tank` until the resilver completes. ZED reports the
   result.
9. Run a scrub once the resilver is done, and update the disk map and smartd
   config in your docs if the device paths changed.

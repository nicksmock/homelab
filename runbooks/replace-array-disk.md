# Replace a failed Unraid array disk

| Value | This lab |
|---|---|
| Server | poseidon, Unraid |
| Array | 2 parity + 2 data, all 10 TB |
| Largest data disk / smallest parity disk | 10 TB / 10 TB |
| Normal parity check time | About 15 hours |

Use this when Unraid has disabled a data or parity disk, or SMART shows a
disk failing. It covers a replacement in the same slot.

## Rules

- A replacement data disk must be no larger than the smallest parity disk.
  A larger one needs Unraid's parity-swap procedure, which is not covered
  here.
- A replacement parity disk must be at least as large as the largest data
  disk.
- Never use **Tools > New Config** for this. It throws away the disabled-disk
  state, and with it the emulated contents of the failed disk.
- Never format the new disk. The rebuild writes the filesystem back from
  parity.
- With dual parity the array survives one more failure during the rebuild,
  but not two. Keep load low until it finishes.

## Before

1. Take a flash backup: **Main > Boot Device > Flash > Flash Backup**, and
   keep the zip off the server.
2. Check that alerts reach you, so the rebuild's progress and any new
   failure are not missed.
3. Pause bulk writers, such as download clients and library imports.
4. Optional: browse the emulated disk at `/mnt/diskN` and check its top-level
   folders look right.
5. Recommended: test the new disk first, for example with an extended SMART
   test in a USB dock.

## Swap

1. **Main > Array Operation > Stop**.
2. Shut down the server and power it off at the wall.
3. Remove the failed disk. Match it by the serial on its label.
4. Check the SATA data cable and power connector on that bay, and replace
   them if there is any doubt. A link that drops or slows down before the
   errors start often points at the cable or connector, not the disk.
5. Install the new disk and boot.
6. In **Main**, select the new disk in the failed slot. Check that every
   other slot still has the right disk, by serial.
7. **Start** the array and confirm the rebuild (or, for a parity slot, the
   parity sync).
8. The rebuild takes about as long as a parity check. The array stays usable
   while it runs.

## After

1. Run **Main > Check** with "Write corrections to parity" unticked. Expect
   0 errors.
2. Check the new disk's SMART: reallocated, pending and CRC counts all 0.
3. Test the old disk in another machine with an extended SMART self-test.
   Keep it as a cold spare only if it passes.
4. Update the disk table in the docs with the new model and the date.

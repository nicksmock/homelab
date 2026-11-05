# Replace a failed Unraid flash drive

| Value | This lab |
|---|---|
| Server | poseidon, Unraid |
| Flash copy | kronos, `/tank/poseidon/flash/`, pulled nightly, with snapshot history |
| What matters on the flash | `config/`: the license key, array layout (`super.dat`), shares, plugins, templates, SSH keys |

Use this when the USB boot drive dies or will not boot. Unraid's license is
tied to the drive, so a new drive also means a license transfer.

## Prepare (before any failure)

1. Keep a spare flash drive from a reputable brand, 8 to 32 GB. Unraid ties
   the license to the drive's unique ID, so it needs a drive that reports
   one.
2. Keep a copy of the flash off the server. Here, kronos pulls the whole
   drive every night.

## Recover

1. Pick the copy to restore. Last night's is `/tank/poseidon/flash/`. If the
   flash was already going bad before that, use a snapshot from before the
   problem: `/tank/poseidon/.zfs/snapshot/<snapshot>/flash/`.
2. Pack `config/` and bring it to your workstation:
   ```bash
   ssh <backup-host> "sudo tar -C /tank/poseidon/flash -czf - config" > flash-config.tgz
   ```
   It holds the license key, password hashes and SSH host keys, so treat it
   as a secret.
3. Write the new drive with the Unraid USB Creator, using the same Unraid
   version as before.
4. Extract the archive and copy its `config/` over the new drive's
   `config/`.
5. Boot the server from the new drive. Before starting the array, open
   **Main** and check every slot against your disk table, by serial. If
   anything does not match, do not start the array. Fix the assignments
   first.
6. Transfer the license in **Tools > Registration > Replace Key**. The
   self-service transfer is limited to about once a year. After that it goes
   through Unraid support.
7. Start the array. Plugins reinstall from the flash, which needs internet
   access, and Docker starts the autostart containers.
8. Check the webGUI, SSH with your key, the containers and the alerts.
9. Delete `flash-config.tgz` from the workstation.

The next nightly pull mirrors the new flash onto kronos. The old flash's
contents stay in the snapshots.

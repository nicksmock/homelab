# Restore one container's appdata

| Value | This lab |
|---|---|
| Server | poseidon, Unraid |
| Appdata | `/mnt/user/appdata/<app>/` |
| Local backups | Appdata Backup plugin, `/mnt/user/backups/appdata/ab_<date>_<time>/`, 3 days |
| Backup host | kronos, ZFS dataset `tank/poseidon`, snapshots under `/tank/poseidon/.zfs/snapshot/` |
| Offsite | restic repository in Backblaze B2 |
| Archive format | One `<container>.tar.gz` per container, holding absolute paths (`/mnt/user/appdata/<app>/...`) |

Use this when one app's config or database is broken. Pick the newest source
that has a good copy:

| Source | Covers | Go to |
|---|---|---|
| poseidon's own backup folder | The last 3 days | Step 3 |
| kronos snapshots | 14 daily, 8 weekly, 6 monthly | Step 1 |
| restic in B2 | 7 daily, 4 weekly, 6 monthly | Step 2 |

## 1. Get the archive from kronos

1. List the snapshots and pick one from before the problem:
   ```bash
   zfs list -t snapshot -o name,creation tank/poseidon
   ls /tank/poseidon/.zfs/snapshot/<snapshot>/appdata/
   ```
2. Pick a run folder in it and find `<container>.tar.gz`.
3. kronos has no way to write to poseidon, by design. Copy the archive
   through your workstation:
   ```bash
   scp -3 <backup-host>:<path>/<container>.tar.gz <server>:/mnt/user/backups/restore-<app>.tar.gz
   ```
   Go to step 4.

## 2. Get the archive from B2

On kronos, or on any machine with restic and the repository credentials.

1. Load the credentials into the environment from your password manager,
   using prompts so nothing lands in shell history:
   ```bash
   read -rp  "B2 key ID: " AWS_ACCESS_KEY_ID; export AWS_ACCESS_KEY_ID
   read -rsp "B2 application key: " AWS_SECRET_ACCESS_KEY; echo; export AWS_SECRET_ACCESS_KEY
   read -rp  "Repository (s3:https://<endpoint>/<bucket>): " RESTIC_REPOSITORY; export RESTIC_REPOSITORY
   read -rsp "restic password: " RESTIC_PASSWORD; echo; export RESTIC_PASSWORD
   ```
2. Find a snapshot and restore only the archive you need:
   ```bash
   restic snapshots
   restic ls <snapshot-id> /tank/poseidon/appdata
   restic restore <snapshot-id> --target ./rr --include /tank/poseidon/appdata/<run>/<container>.tar.gz
   ```
3. Copy it to poseidon with `scp`, then close the shell so the credentials go
   with it. Go to step 4.

## 3. Use poseidon's own copy

Use the Appdata Backup plugin's **Restore** tab, or take the archive straight
from `/mnt/user/backups/appdata/<run>/` and go to step 4.

## 4. Restore on poseidon

1. In the **Docker** tab, stop the container.
2. Set the current folder aside. Don't delete it yet:
   ```bash
   mv /mnt/user/appdata/<app> /mnt/user/appdata/<app>.bad-$(date +%Y%m%d)
   ```
3. Extract in place. The archive holds absolute paths, and tar strips the
   leading `/`:
   ```bash
   tar -xzf /mnt/user/backups/restore-<app>.tar.gz -C /
   ```
4. Start the container, then check its UI and logs.
5. When it works, delete the `.bad-` folder and every copy of the archive you
   made along the way. The archives hold the app's API keys.

If the container itself has to be recreated, its template (`my-<name>.xml`)
is in the same run folder. Copy it to
`/boot/config/plugins/dockerMan/templates-user/`, then use
**Apps > Previous Apps**.

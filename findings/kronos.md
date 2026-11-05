# kronos: closed findings

Findings from the October and November 2026 audit of kronos that are fixed or
accepted. How the audit worked is in [METHODOLOGY.md](../METHODOLOGY.md), and
the host's current state is in [systems/kronos.md](../systems/kronos.md).

## High

### Backups never restored

Severity: high. Status: fixed 2026-11-04

What I found: nothing on kronos showed that a backup had ever been restored.
There was no database check, no restic restore and no repository check, and
the failure alert had never been tested. The restic password and B2 keys were
only on kronos.

Why it mattered: a backup that has never been restored is a hope, and
without those secrets stored elsewhere, losing kronos would have made the
offsite copy unreadable.

What I changed: I put the recovery secrets in my password manager and ran
every restore test, from a snapshot extract up to restoring an app into a
temporary container.

How I verified it: the database check passed, the B2 restore matched the
local copy's checksum, `restic check` found no errors, the forced failure
alert arrived, and the restored app's data matched the live app.

## Medium

### A missing pool would have looked like success

Severity: medium. Status: fixed 2026-11-03

What I found: if the pool wasn't mounted at 05:00, the job would have written
the backup to the boot disk, uploaded that and reported success. That nearly
happened when the USB enclosure didn't power back on after an outage.

Why it mattered: the backups would have quietly stopped while every run
looked fine.

What I changed: the job now stops with an error unless the backup dataset is
mounted. After a power loss I power the enclosure on and import the pool by
hand.

How I verified it: the check is at the top of the job, the pool was back and
mounted, and the next scheduled run succeeded.

### Silence looked like success

Severity: medium. Status: fixed 2026-11-04

What I found: alerts fired only when the job failed. If kronos was off, the
timer stopped, or the network was down, nothing would tell me. The snapshot
health checks weren't wired to anything.

Why it mattered: the most likely ways for backups to stop are the ones that
make no noise.

What I changed: the job pings Uptime Kuma on poseidon at the end of every
successful run, and Uptime Kuma alerts if a ping is missed. A daily timer runs
sanoid's snapshot and pool checks and alerts on failure. Uptime Kuma is
silent if poseidon, the power or the internet is down, which I accepted.

How I verified it: the heartbeat arrived after the next run, and the monitor
checks passed.

### The pull key could run more than the pull

Severity: medium. Status: fixed 2026-11-04

What I found: the forced command for kronos's key on poseidon accepted any
rsync options. Some rsync options write files on the server side.

Why it mattered: anyone with the kronos key could have used it to write to
poseidon, not just read from it.

What I changed: the forced command now allows only the two exact rsync
commands the job uses.

How I verified it: the nightly job ran with status 0, and a different
command with the same key was refused.

### One compromise reaches every copy

Severity: medium. Status: accepted 2026-11-05

What I found: root on kronos can delete the local snapshots, and kronos's B2
key can delete the offsite copy and change the bucket's settings.

Why it mattered: an attacker on kronos could destroy all the history at once.

What I changed (or why I accepted it): I set B2 to keep hidden versions for
30 days, so anything restic prunes stays recoverable. A key without delete
rights needs restic's native B2 backend, and B2 refused that backend's
sign-in with a restricted key. B2's object lock doesn't fit how restic works.
So kronos keeps its current key, and I'll revisit this when restic supports
B2's newer API.

How I verified it: the 30-day setting is on the bucket, and the nightly job
still runs with the current key.

### Admin access on the backup host

Severity: medium. Status: accepted 2026-11-04

What I found: my account has passwordless sudo, and keys from a few of my
devices can log in. Each of them is effectively root on the host that holds
every backup and the B2 key.

Why it mattered: the backup host should be the hardest machine to get into.

What I changed (or why I accepted it): I keep a key synced in my SSH app so I
can reach the lab from any device, and a separate key as a fallback when that
app's service is down. The rest stays for the documentation work.

How I verified it: SSH still accepts keys only, and root can't log in over
SSH.

### One enclosure for both mirror disks

Severity: medium. Status: accepted 2026-11-03

What I found: both disks of the mirror share one USB bridge, one cable and
one power supply. A fault there drops the whole pool.

Why it mattered: the mirror protects against a disk failing, not the
enclosure.

What I changed (or why I accepted it): kronos holds the second of three
copies, and B2 holds the third, so I accepted it.

How I verified it: the pool is healthy, and the kernel log shows no USB
resets.

## Low

### No TRIM through the enclosure

Severity: low. Status: accepted 2026-11-03

What I found: the USB bridge doesn't pass TRIM to the SSDs, so automatic TRIM
is off.

Why it mattered: without TRIM, SSD write speed can drop over time.

What I changed (or why I accepted it): nightly writes are small, so I accepted
it. I'll revisit if a heavier workload moves onto the pool.

How I verified it: the pool's autotrim setting is off on purpose.

### Unlabeled drive bays

Severity: low. Status: fixed 2026-11-03

What I found: which bay held which disk was only in the docs.

Why it mattered: replacing the wrong disk in a mirror loses the pool.

What I changed: I labeled both bays.

How I verified it: by looking at the labels myself.

### restic ran without a cache

Severity: low. Status: fixed 2026-11-03

What I found: the job's service didn't set a home folder, so restic ran with
no local cache and re-read metadata from B2 every night.

Why it mattered: slower runs and more B2 reads.

What I changed: I set the home folder in the service.

How I verified it: the next run finished in 8 minutes with no cache warning.

### Backups bigger than planned

Severity: low. Status: fixed 2026-11-03

What I found: the appdata plugin kept 7 days of runs, not 3, and most of
each run was the media server's cache and metadata, which it rebuilds on its
own.

Why it mattered: local and B2 storage were heading to about three times what
I had planned.

What I changed: I set the plugin to 3 days and excluded the media server's
cache and metadata folders.

How I verified it: the next run was 1.6 GB, with the media server's database
in it and no cache or metadata, and the oldest run was deleted.

### A webhook in a world-readable file

Severity: low. Status: fixed 2026-11-03

What I found: the ZFS event daemon's config, which holds the Discord webhook,
was readable by every user.

Why it mattered: anyone on the host could post as my alerts.

What I changed: I made it readable by root only.

How I verified it: the file is mode 600.

### One alert attempt, no retry

Severity: low. Status: fixed 2026-11-03

What I found: the alert script sent once, with no retry, and mail to root
went nowhere.

Why it mattered: a brief network blip could lose an alert.

What I changed: the alert script retries three times.

How I verified it: the retry is in the script.

### root had a password

Severity: low. Status: fixed 2026-11-03

What I found: root had a password set, though the build notes said it was
left blank.

Why it mattered: an unneeded password is one more thing to guess or leak.

What I changed: I locked root's password.

How I verified it: root's account shows as locked.

### An aging boot disk with no mirror

Severity: low. Status: accepted 2026-11-05

What I found: the boot disk has about 35,000 power-on hours and no mirror.

Why it mattered: if it fails, kronos is down until rebuilt.

What I changed (or why I accepted it): kronos can be rebuilt from my notes,
its restores are proven, and the recovery secrets are in my password manager.
The backups themselves are on the pool and in B2, not on the boot disk.

How I verified it: the restore tests above.

### Stable updates not automatic

Severity: low. Status: fixed 2026-11-05

What I found: unattended-upgrades applied security updates only, not
Debian's stable updates.

Why it mattered: bug fixes waited for a manual update.

What I changed: I enabled the stable updates origin. Automatic reboots stay
off, so after a kernel update I reboot by hand and check the pool.

How I verified it: the origin is enabled in the config.

### A daily check that clashed with sanoid

Severity: low. Status: fixed 2026-11-05

What I found: the daily snapshot and pool check started in the same second as
sanoid's own run, failed on sanoid's lock, and sent a false alarm.

Why it mattered: false alarms teach you to ignore real ones, and the pool
check never ran that day.

What I changed: I moved the check to a few minutes past the hour, off
sanoid's schedule.

How I verified it: a run at the new minute passed both checks.

### SMART monitoring stopped after an outage

Severity: low. Status: fixed 2026-11-05

What I found: smartd had been stopped for three days. It exits at boot if a
disk it watches is missing, and the enclosure was off after a power cut.

Why it mattered: no disk health checks or alerts, for the boot disk as well.

What I changed: I restarted it and marked the pool disks as removable, so an
absent enclosure no longer stops it. The power loss steps now include
restarting it.

How I verified it: smartd is running and watching all three disks.

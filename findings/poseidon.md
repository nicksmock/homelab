# poseidon: closed findings

Findings from the October and November 2026 audit of poseidon that are fixed or accepted.
Each one was re-verified on the live server before it was closed. How the
audit worked is in [METHODOLOGY.md](../METHODOLOGY.md), and the server's
current state is in [systems/poseidon.md](../systems/poseidon.md).

## High

### A failed data disk, undetected for eight weeks

Severity: high. Status: fixed 2026-10-20

What I found: Unraid had disabled disk1, a 10 TB HGST, on 2026-08-23, and had
been emulating it from parity ever since, about 55 days. The kernel log showed
the order of events. The SATA link dropped and came back at 3.0 Gb/s instead
of 6.0 Gb/s, and only then did reads fail and the device get disabled. SMART
could not be read at all. The parity disk and the other data disk are the
same model as the failed one, and were very likely bought together.

Why it mattered: dual parity was already spending one of its two disks of
margin. One more failure would have left the array with no redundancy, and a
second would have lost data. Nobody knew, because the alerts never left the
server (see the next finding).

What I changed: I replaced disk1 with another 10 TB HGST of the same model.
When I pulled the old drive, the plastic around its SATA power pins had
crumbled, which fits the link drops, so I retired that drive and replaced the
power cable as well. Unraid then rebuilt the new disk from parity, and I ran a
full non-correcting parity check afterwards. The old drive itself was never
tested, so the connector is the likely cause rather than a confirmed one.

How I verified it: the rebuild finished in about 15 hours with 0 errors. The
non-correcting check of both parity disks then completed with 0 errors. It
took 28 hours instead of the usual 15 because downloads kept running. After
the check, disk1 showed as healthy with a 6.0 Gb/s link and clean SMART, and
the array reported 0 disabled, invalid or missing disks.

### Alerts that never left the server

Severity: high. Status: fixed 2026-10-17

What I found: every Unraid notification level (normal, warning and alert)
was set to show in the webGUI only. A Discord agent was installed, but no
notification level used it. The disk1 failure and a weekly Fix Common Problems warning about it had
been sitting in the webGUI, among 130 unread notifications. A custom
array-health-monitor script that ran every 5 minutes could not catch the
failure either:

- It looked for strings that never appear in Unraid's disk status lines, so
  its per-disk check could never fire.
- It did not read the counts of disabled, invalid or missing disks.
- It kept no state, so anything it did catch would re-alert every 5 minutes.
  A rebuild would have posted about 12 times an hour for its whole run.
- It did not check whether the post to Discord succeeded.

Why it mattered: this is why a failed disk went unnoticed for eight weeks.

What I changed: I turned on agent delivery for the warning and alert levels,
so those go to Discord as well as the webGUI. I replaced the script with a
rewritten one that reads the disabled, invalid and missing counts and each
disk's status and error count. It keeps state so a problem posts once, and it
records an alert as sent only after Discord accepts it.

How I verified it: the notification settings showed agents enabled for
warning and alert. The script on the server matched the reviewed copy. Its
first run, with disk1 still disabled, reported the disabled and invalid disk,
disk1's status and its read and write error count, and posted one critical
alert, which arrived in Discord. The error count had not been recorded
anywhere before.

### No backup outside the server

Severity: high. Status: fixed 2026-11-04

What I found: the only backup was a nightly script that archived the live
appdata folder to the same array it was backing up. It copied databases while
the apps were writing to them, missed Docker volumes, and included a copy of
the system password file in a share. The Appdata Backup plugin was installed
but never configured.

Why it mattered: a failed array, a ransomware hit or a bad flash drive would
have taken the backups with the data, and a database copied mid-write may not
restore at all.

What I changed: I configured the Appdata Backup plugin, which stops each
container before it archives it. A separate backup host, kronos, now pulls
those archives and the whole flash drive every night, keeps snapshot history
and sends a copy to Backblaze B2. I disabled the old script and deleted its
output, including the password file copy.

How I verified it: I restored an app from a kronos snapshot into a temporary
container and checked its database and data against the live app. I also
restored a file from B2 and compared checksums, and ran a repository check.

### Every share open to the LAN

Severity: high. Status: fixed 2026-11-04

What I found: every share was public, and four were exported over SMB with no
login. One of them was appdata, which held the reverse proxy's TLS private
key, readable by anyone, an old app's `.env` with a database password and an
API key, and every app's config and database.

Why it mattered: any device on the home network, including a compromised one,
could read or change every app's data and take the proxy's private key.

What I changed: I stopped exporting appdata and the media and data shares,
deleted a share I no longer used, and made the one share that still needs SMB
private to a single named user. I set the key files to owner-only.

How I verified it: the live Samba config offered only that one share, a guest
login was refused, and the key files were mode 0600.

### Every route published by default

Severity: high. Status: fixed 2026-11-05

What I found: the tunnel and DNS used a wildcard, so every Traefik route was
public as soon as it existed. That included the DNS resolver's admin UI.

Why it mattered: adding a route for a local-only tool would have published
it on the internet without any further step.

What I changed: I moved the DNS admin UI off the tunnel, then replaced the
wildcard with one explicit tunnel route and DNS record for each app that
should be public. Details are in the [Cloudflare findings](cloudflare.md).

How I verified it: the published apps answered as before, and a made-up
hostname no longer resolved.

### CrowdSec could not tell visitors apart

Severity: high. Status: fixed 2026-11-04

What I found: Traefik logged every request from the tunnel with the tunnel
container's address, so a ban would have blocked every remote user at once.
CrowdSec was also reading the wrong path for Traefik's access log, so it saw
no traffic at all.

Why it mattered: the intrusion detection was in place on paper but could
neither detect nor block a real attacker.

What I changed: I set Traefik to trust forwarded client addresses from the
tunnel's network, fixed the log path in CrowdSec's acquisition config, and
later replaced the old standalone bouncer, which looked unmaintained, with
the maintained CrowdSec plugin inside Traefik.

How I verified it: Traefik's log and CrowdSec's lookups showed real client
addresses. A five-minute test ban on a phone's address returned 403 on two
apps, and access came back when it expired.

### Docker image filled up

Severity: high. Status: fixed 2026-11-03

What I found: the Docker image had filled to 100% once already. 13 GB of it
was orphaned volumes from a download client that staged files inside the
image, including a few finished downloads that never reached the library.

Why it mattered: a full Docker image stops every container, and the staging
design meant it could happen again.

What I changed: I removed that download client, rescued the stranded
episodes into the library, and deleted the unattached volumes and old
templates.

How I verified it: no unattached volumes remained, and the library showed the
rescued episodes.

## Medium

### SSH accepted password logins

Severity: medium. Status: fixed 2026-10-18

What I found: the SSH config did not set `PasswordAuthentication`, so the
OpenSSH default applied and the admin account could log in with a password,
even though key login was already in use.

Why it mattered: password login allows password guessing against the account
with full control of the server.

What I changed: I switched SSH to key-only in Unraid's management access
settings.

How I verified it: the running SSH config showed `passwordauthentication no`
and `kbdinteractiveauthentication no`, and it matched the persistent config on
the flash drive. A login attempt offering only a password was refused with
"Permission denied (publickey)".

### Broken routes and dead services

Severity: medium. Status: fixed 2026-10-17

What I found: several public routes and containers were broken or
half-configured:

- The dashboard's route returned 502. Its Traefik label pointed at the
  host port instead of the port the container listens on.
- The route for Tunarr returned 500. It depended on a forward-auth service
  that had crashed with a config error almost three months earlier, so the
  route failed closed.
- A metadata companion container had been created but never started.
- The route for the DNS admin UI returned 502 at the time of the test.
- A router for a placeholder hostname could never match anything.

Why it mattered: public routes pointed at broken backends, and the auth
layer that one route depended on had been down for almost three months
without anyone knowing.

What I changed: I didn't need the dashboard or Tunarr reachable from outside,
so I removed both routes, and the dashboard container with them. I removed
the crashed auth service, the unused companion container and the placeholder
router. I also removed the DNS admin UI's routes from Traefik, so it is no
longer published, and put Cloudflare Access in front of its hostname.

How I verified it: the Traefik API listed only the intended app routes and
its internal ones. The removed hostnames returned 404 from Traefik, and the
removed containers no longer existed.

### Parity checks skipped for three months

Severity: medium. Status: fixed 2026-10-20

What I found: the parity check history had no runs from April to June 2026.
The cause could not be determined from the server. Two earlier runs had each
reported a single sync error: one in September 2025, and one in a run aborted
in July 2026. The September and October 2026 checks did run, but with disk1
disabled, so they could not check that disk.

Why it mattered: parity that has not been checked may not rebuild a disk
correctly when it is needed.

What I changed: after the disk1 rebuild, I ran a full non-correcting check of
both parity disks, and confirmed that the monthly schedule fires.

How I verified it: the check completed on 2026-10-20 after 28 hours with 0
errors. The parity history shows the scheduled checks ran on the first
Sundays of September and October.

### Clock and time zone

Severity: medium. Status: fixed 2026-10-17

What I found: NTP was disabled, and the server clock was about 40 seconds
fast. The server's time zone was three hours off the site's, so every schedule
on the server, including the parity check, the mover and the scheduled
scripts, ran three hours later local time than it was configured for. The
server's address came from DHCP with no static fallback.

Why it mattered: maintenance ran three hours later than intended, and the
clock drifted with nothing to correct it.

What I changed: I enabled NTP and set the server to the site's time zone. For
the address, I confirmed that the gateway has a DHCP reservation for
poseidon.

How I verified it: ntpd was running and reaching two stratum-2 peers with
offsets of a few milliseconds, and the time zone showed the site's zone. The
reservation for 10.0.20.10 was read from the gateway's config.

### An unused development stack

Severity: medium. Status: fixed 2026-10-18

What I found: a side project I no longer used was still running as three
containers: a database, a backend and a frontend. The backend and frontend
ran development servers with live reload, each published on a host port. The
project's secrets, a database password and an API key for an external AI
service, sat in a world-readable `.env` file. A privileged BuildKit
container, left over from building the project's images, was also still
running.

Why it mattered: development servers and a privileged container add attack
surface for no benefit, and any process or user that could read the file
could use the API key.

What I changed: I removed the stack's containers, volumes, network, images and
folder, removed the BuildKit container, and revoked the API key.

How I verified it: no containers, volumes, images or network from the stack
or BuildKit remained, and the project folder was gone. The key was revoked
in the provider's console, which the server cannot show, so that part is
reported by me rather than verified.

### The reverse proxy could control Docker

Severity: medium. Status: fixed 2026-11-05

What I found: Traefik mounted the Docker socket so it could read container
labels. Mounting it read-only does not limit the Docker API, so anyone who
took over Traefik could control every container and the host. Two other
containers had the same access, one of them running as root.

Why it mattered: Traefik is the one container that handles traffic from the
internet, so it is the most likely to be attacked.

What I changed: I removed the two other containers, which I no longer needed.
Traefik now talks to a socket proxy instead of the socket. The proxy runs
unprivileged and read-only, publishes no ports, and answers only Traefik,
and only for the few read requests its Docker provider makes.

How I verified it: Traefik had no socket mount and still built its routes.
A request to the proxy from anywhere else got 403.

### Admin ports open to the LAN

Severity: medium. Status: accepted 2026-11-04

What I found: there is no host firewall, and every published container port
listened on all interfaces. That included metrics endpoints, the CrowdSec
API, an exporter and the Traefik dashboard, which has no login.

Why it mattered: nothing is forwarded from the internet, so the exposure was
limited to the local network, but it was more than any of these needed.

What I changed (or why I accepted it): I stopped publishing the ports that
only other containers use, and removed the exporter. I kept the Traefik
dashboard reachable on the LAN, because I use it for troubleshooting.

How I verified it: the removed ports no longer answered, and the tunnel and
CrowdSec kept working.

### Crashed containers stayed down

Severity: medium. Status: fixed 2026-11-04

What I found: every container had the restart policy `no`, and a few were
missing from Unraid's autostart list, so a crash or a reboot could leave
services down until someone noticed.

Why it mattered: DNS, the tunnel and the media apps could all go down
silently.

What I changed: I set `--restart unless-stopped` in every container's
template, so it survives updates, and added the missing containers to
autostart.

How I verified it: every container reported `unless-stopped` and was running,
and the templates still parsed.

### Images float on latest

Severity: medium. Status: accepted 2026-11-05

What I found: almost every image used `latest` or no tag, so an update could
bring a new major version without warning.

Why it mattered: a breaking change in Traefik in particular would take every
public app down at once.

What I changed (or why I accepted it): I pinned Traefik to its current major
version. I left the other images floating, because they are current, a bad
update affects only one app, and the nightly backups make a rollback easy.

How I verified it: Traefik ran on the pinned tag, and the public apps
answered.

### Unrotated access log

Severity: medium. Status: fixed 2026-11-04

What I found: Traefik's access log had grown to 1.45 GB with no rotation, and
it was part of every appdata backup.

Why it mattered: it wasted cache space and made every backup larger.

What I changed: a scheduled script rotates the log nightly once it passes
50 MB and keeps about a week of compressed copies. The log folder is
excluded from the backup.

How I verified it: the first run compressed 1.47 GB to 96 MB, Traefik wrote a
fresh log, and CrowdSec reopened it.

### A subtitle app with no login

Severity: medium. Status: fixed 2026-11-04

What I found: the subtitle manager had authentication turned off, so anyone
who could reach it could read the API keys it holds for two other apps.

Why it mattered: those keys give full control of the TV and movie managers.

What I changed: I turned on form login. The first save stored an empty
password and locked the UI, so I reset it and checked the stored password's
length before trusting it.

How I verified it: its API returned 401 without a login, and logging in
worked.

## Low

### A Docker network expected to vanish on restart

Severity: low. Status: accepted 2026-10-18

What I found: while writing the recovery runbooks, the audit flagged that
Unraid's Docker setting for user-defined networks was set to remove them. If
that applied to the bridge network that Traefik and most containers share,
the network would disappear on every Docker restart, and those containers
would not start until it was recreated by hand.

Why it mattered: it would have turned every reboot into a manual recovery.

Why I accepted it: the finding was wrong. Unraid's start script applies that
setting only to the macvlan and ipvlan networks it names after host
interfaces. Ordinary bridge networks are stored in the Docker image and are
never removed. No change was needed. The runbooks keep the step that creates
the network, because a new Docker image starts without it.

How I verified it: after a reboot on 2026-10-18, the bridge network was still
present with its original creation date and all of its containers attached.

### Duplicate and broken plugins

Severity: low. Status: fixed 2026-11-04

What I found: deprecated plugins ran next to their replacements, one plugin
was stuck in an error state, and two others came from outside Community
Applications, one of them tracking a development branch.

Why it mattered: unmaintained plugins run as root on the host.

What I changed: I removed the deprecated plugins, cleared the stuck one, and
removed the two outside plugins I no longer needed. I kept the one that runs
the monthly Recyclarr sync.

How I verified it: the removed plugins left no files, cron entries or web UI
pages behind.

### Leftovers from removed apps

Severity: low. Status: fixed 2026-11-05

What I found: configs for shares that no longer existed, 50 unused container
templates, orphaned Docker networks and images, app folders for removed apps,
and old download folders with about 55 GB of files nothing used.

Why it mattered: clutter hides what is really in use and wastes space.

What I changed: I deleted the leftovers after checking that no app pointed at
them.

How I verified it: each path was gone, every container kept running, and only
one unused template remained.

### Inconsistent container settings

Severity: low. Status: fixed 2026-11-04

What I found: containers used four different time zones, one ran as a
different user from the rest, the request app logged at debug level, CrowdSec
loaded a collection for software I don't run, and Jellyfin published a wrong
URL and discovery ports that cannot work from a bridge network.

Why it mattered: mismatched times make logs hard to line up, and the extra
ports and debug logging added noise for nothing.

What I changed: one time zone and one user for every container, info-level
logging, the unused collection removed, and Jellyfin's URL and ports fixed.

How I verified it: each container's settings matched, and Jellyfin answered on
its corrected URL.

### Restore runbook never tested

Severity: low. Status: fixed 2026-11-04

What I found: none of the server's runbooks had been tested, and the restore
steps pointed at the old backup script.

Why it mattered: an untested restore is a guess.

What I changed: I rewrote the restore steps for the Appdata Backup archives
and restored an app from a backup copy into a temporary container.

How I verified it: the restored database passed an integrity check and its
data matched the live app. The step that swaps a restored folder into a live
container was not part of the drill.

### Two hardware addresses for one IP

Severity: low. Status: accepted 2026-11-05

What I found: the gateway sees two hardware addresses for the server's IP,
because Docker's host access to custom networks adds a second interface.

Why it mattered: it can confuse DHCP reservations and client lists.

What I changed (or why I accepted it): I kept it. The server needs that
setting to reach the second DNS resolver, which runs on a macvlan network on
the same host.

How I verified it: both DNS resolvers answer, and the server's reservation
still works.

### DNS sync API open to the LAN

Severity: low. Status: fixed 2026-11-04

What I found: the container that syncs the two DNS resolvers published its
API with no login, so any device on the LAN could trigger a sync. It and the
second resolver also ran untagged images with no restart policy.

Why it mattered: a crash would have left the second resolver or its sync down
until someone noticed.

What I changed: I turned the sync API off and removed its port, pinned both
images, and set them to restart unless stopped.

How I verified it: no port was published, a sync completed, and both
resolvers answered.

### Repair files on the flash drive

Severity: low. Status: fixed 2026-11-03

What I found: 19 filesystem repair files, the largest 178 MB, sat on the
flash drive, showing it had been repaired at least once.

Why it mattered: they wasted space on a small drive and were a sign of past
trouble.

What I changed: I deleted them once kronos held a nightly copy of the whole
flash drive.

How I verified it: none were left on the flash drive.

### Client tokens in the proxy log

Severity: low. Status: accepted 2026-11-05

What I found: Traefik's access log records full request URLs, and the Jellyfin
apps put their session token in the query string of one request.

Why it mattered: anyone who reads the logs or their backups can reuse a
client's session.

What I changed (or why I accepted it): Traefik has no setting to drop only
the query string, and CrowdSec needs the access log. I treat the logs and
their backups as secret, and sign out a client session if its log line ever
leaves the server.

How I verified it: the logs stay on the server and in its own backups.

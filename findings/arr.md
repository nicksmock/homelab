# arr: closed findings

Findings from the November 2026 audit of Sonarr, Radarr, Prowlarr and the
comics manager that are fixed or accepted. How the audit worked is in
[METHODOLOGY.md](../METHODOLOGY.md), and the current configuration is in
[systems/arr.md](../systems/arr.md).

## Medium

### Library folders out of step with Radarr

Severity: medium. Status: fixed 2026-11-04

What I found: Radarr's root folders held 11 folders it didn't track, about
78 GB. Three movies had files in one root while Radarr tracked them as
missing in another, three had a second copy in another root, four weren't in
Radarr at all, and one folder was empty.

Why it mattered: Radarr would have downloaded the three "missing" movies
again, and the duplicates wasted almost 40 GB.

What I changed: I pointed Radarr at the existing files, kept one copy of each
duplicate, imported the untracked movies and removed the empty folder.

How I verified it: every Radarr root showed no unmapped folders, and the
three movies showed their files.

### No recycle bin

Severity: medium. Status: fixed 2026-11-03

What I found: neither Sonarr nor Radarr had a recycle bin, so a file they
deleted or replaced during an upgrade was gone for good.

Why it mattered: a bad upgrade or a mistaken delete couldn't be undone.

What I changed: both apps move removed files to a recycle bin in the data
tree and clear it after 7 days.

How I verified it: the setting read back from both apps.

### The comics manager flooded the indexers

Severity: medium. Status: fixed 2026-11-04

What I found: Pullbox made about half of Prowlarr's recent searches, in
bursts across every indexer and category, and drew rate-limit errors from an
indexer the TV and movie managers also use. It also kept stale entries for
indexers I had removed, and a direct search entry that failed every time.

Why it mattered: one app's searches could get the shared indexers to
throttle every app.

What I changed: I resynced Pullbox's indexers so it uses only the three
usenet indexers, in book and comic categories, and removed the failing
entry. Most of the bursts came from imports failing and retrying, which is
the next finding.

How I verified it: a search ran through the three indexers with no errors,
and Prowlarr's history showed only those categories from Pullbox.

### Indexer tokens in the comics manager's log

Severity: medium. Status: accepted 2026-11-04

What I found: when an NZB download fails, Pullbox logs the full URL,
including the indexer's API token, and those logs are in the backups.

Why it mattered: anyone who reads the logs can use my indexer account.

What I changed (or why I accepted it): Pullbox has no setting to redact URLs
or lower its log level. The logs stay on the server and in my own backups,
so I treat them as secret and will rotate the token if they ever leave.

How I verified it: no redaction setting exists in its config or environment.

### Usenet first, but only as a tie-break

Severity: medium. Status: fixed 2026-11-03

What I found: usenet was preferred only when two releases were otherwise
equal. A torrent with a better score could still win.

Why it mattered: torrents were meant to be a fallback, not a competitor.

What I changed: I removed the torrent path entirely
([decision 0011](../decisions/0011-usenet-only.md)).

How I verified it: NZBGet is the only download client, and Prowlarr has only
usenet indexers.

### Hundreds of failed downloads

Severity: medium. Status: accepted 2026-11-04

What I found: Sonarr listed 825 failed downloads and Radarr 44, with a few
series failing again and again, plus hundreds of missing episodes.

Why it mattered: it looked like a loop wasting indexer quota and bandwidth.

What I changed (or why I accepted it): the review showed it wasn't a loop.
Almost all the failures were releases too incomplete on usenet to finish,
rejected by NZBGet's health check, in one-day bursts when a series was added.
Season packs count once per episode, which inflated the numbers. Each bad
release was blocklisted and the next one tried, and every one of those series
is now complete. I keep missing titles monitored, with no extra searches.

How I verified it: no new failures since the last burst, and the apps' only
indexer traffic was RSS.

### An old comics app still synced

Severity: medium. Status: fixed 2026-11-03

What I found: Prowlarr still synced indexers to the comics app I had
replaced, and the sync timed out on every run.

Why it mattered: a health warning that keeps coming back hides real ones.

What I changed: I removed it from Prowlarr.

How I verified it: Prowlarr lists only Sonarr and Radarr, and the warning
cleared.

### The comics manager wouldn't come back after a reboot

Severity: medium. Status: fixed 2026-11-03

What I found: Pullbox wasn't in Unraid's autostart list.

Why it mattered: after a reboot, comics would quietly stop.

What I changed: I added it to autostart, and later every container got a
restart policy.

How I verified it: it is in the autostart list.

### Full-admin API keys

Severity: medium. Status: accepted 2026-11-05

What I found: each app has a single API key with full admin rights, and no
way to make a read-only one.

Why it mattered: anything that holds a key can change or delete the
library's settings.

What I changed (or why I accepted it): the apps offer no scoped keys. I keep
the keys out of the docs and limit where they're stored.

How I verified it: none of the apps offers a key scope.

### No Recyclarr schedule

Severity: medium. Status: fixed 2026-11-03

What I found: Recyclarr, which keeps the profiles in line with the TRaSH
Guides, had no schedule, so the profiles had drifted since summer.

Why it mattered: the profiles would never pick up the guides' updates.

What I changed: Recyclarr runs monthly, and I ran a preview and a sync first
so the first scheduled run wouldn't change everything at once.

How I verified it: the schedule is in cron, and both apps' sync state updated.

### Comics never imported

Severity: medium. Status: fixed 2026-11-04

What I found: every one of Pullbox's import attempts had failed. NZBGet
reported a download path that didn't exist inside Pullbox's container, so
Pullbox never saw the files and kept downloading the same issues.

Why it mattered: comics never reached the library, and the repeat downloads
hit the indexers' limits.

What I changed: I set Pullbox's path mapping for NZBGet and switched its
import method to move, so it also cleans up the download folder. Getting
there exposed a file ownership problem, which I fixed by giving Pullbox a
shared group with NZBGet rather than changing who owns the data.

How I verified it: the next downloads imported, the library had the new
files, and the download folder was empty afterwards.

## Low

### A large first sync waiting

Severity: low. Status: fixed 2026-11-03

What I found: Recyclarr's state was months old, so its first scheduled sync
could have changed many scores at once.

Why it mattered: a surprise change to every profile is hard to untangle.

What I changed: I previewed the sync, found the changes small, and ran it.

How I verified it: both apps' sync state updated.

### A slow, failing indexer

Severity: low. Status: fixed 2026-11-03

What I found: one indexer had never produced a grab, answered slowly and was
failing.

Why it mattered: it slowed every search for nothing.

What I changed: I removed it from all three apps.

How I verified it: it was gone and health was clear.

### Propers always preferred

Severity: low. Status: fixed 2026-11-03

What I found: both apps always preferred propers and repacks, while the
custom formats also scored them, which the TRaSH Guides advise against.

Why it mattered: the two settings could fight and cause needless upgrades.

What I changed: the apps no longer prefer them, and the custom formats decide.

How I verified it: the setting read back from both apps.

### Rescans waking the array

Severity: low. Status: fixed 2026-11-03

What I found: both apps rescanned the disk after every metadata refresh.

Why it mattered: each rescan can spin up the array's disks.

What I changed: they rescan only after a manual refresh.

How I verified it: the setting read back from both apps.

### Debug logs and analytics

Severity: low. Status: fixed 2026-11-03

What I found: all three apps logged at debug level and sent analytics.

Why it mattered: debug logs are noisy and can hold more detail than needed.

What I changed: info level and analytics off in all three.

How I verified it: the settings read back from all three.

### Kids titles in adult folders

Severity: low. Status: accepted 2026-11-05

What I found: a few titles rated for kids were in the adult roots, because
one profile covers both and the root is chosen when a title is added.

Why it mattered: kids' libraries could miss titles meant for them.

What I changed (or why I accepted it): I reviewed each one. The ones left in
place are there on purpose.

How I verified it: the kids roots hold nothing rated PG-13 or above.

### Leftover downloads

Severity: low. Status: fixed 2026-11-04

What I found: finished downloads that never imported sat in the completed
folder, including one stuck in Sonarr's queue and a large release with only
a sample unpacked.

Why it mattered: wasted space, and a stuck queue item blocks attention.

What I changed: I cleared the queue items and the leftover folders.

How I verified it: both queues and the completed folder were empty.

### Torrent indexers with no grabs

Severity: low. Status: fixed 2026-11-03

What I found: several torrent indexers had almost no grabs despite heavy RSS
use, and two were returning errors.

Why it mattered: more noise and load for no benefit.

What I changed: I removed them along with the torrent path.

How I verified it: they were gone from all three apps and health was clear.

### An episode with no media info

Severity: low. Status: accepted 2026-11-04

What I found: Sonarr couldn't read the media info for one episode, which can
mean a damaged file.

Why it mattered: a damaged file fails when someone tries to watch it.

What I changed (or why I accepted it): I played it and it works, so I kept
it.

How I verified it: it played through.

### x265 HD releases rejected

Severity: low. Status: accepted 2026-11-05

What I found: the profiles reject 1080p x265 releases outright, so a title
that only exists in that format stays missing.

Why it mattered: some titles might never download.

What I changed (or why I accepted it): the failed downloads review showed
this wasn't the cause of the missing titles, so the profile stays as the
guide sets it.

How I verified it: the review above.

### A torrent backup path

Severity: low. Status: fixed 2026-11-03

What I found: a debrid torrent client was the second download path, under
two different names in the two apps.

Why it mattered: it had made only a handful of grabs, for an extra service
and credential to keep.

What I changed: I retired it
([decision 0011](../decisions/0011-usenet-only.md)).

How I verified it: it was gone from both apps and the container was removed.

### Server-side items found from the apps

Severity: low. Status: accepted 2026-11-05

What I found: the comics manager had read-write access to the whole data
tree and to the old comics app's folder, the Recyclarr config on the flash
drive holds the TV and movie managers' API keys, and there were stray files in
the data tree.

Why it mattered: wider access than an app needs, and keys in one more place.

What I changed (or why I accepted it): I narrowed Pullbox's mounts to its
library and download folder, removed the old app's folder, and cleaned up the
stray files. The Recyclarr config stays on the flash drive, readable by root
only.

How I verified it: Pullbox's mounts, and the cleanup on poseidon.

### Comics category not in the log

Severity: low. Status: accepted 2026-11-03

What I found: Pullbox's log didn't show a category on its downloads, though
they landed in the comics folder.

Why it mattered: it wasn't clear how they got there.

What I changed (or why I accepted it): the category is set in Pullbox's
settings, which explains it.

How I verified it: in Pullbox's settings.

### An old .NET runtime

Severity: low. Status: accepted 2026-11-05

What I found: Sonarr's image runs on a .NET version that is past end of
support.

Why it mattered: an unsupported runtime gets no security fixes.

What I changed (or why I accepted it): it comes with the current image and
only the upstream project can change it.

How I verified it: Sonarr reports its runtime version.

### Imports from the incomplete folder

Severity: low. Status: accepted 2026-11-05

What I found: some October imports came from NZBGet's incomplete folder, and
I couldn't find why.

Why it mattered: importing from there can pick up a partial file.

What I changed (or why I accepted it): none since the end of October, so I'll
look again if it comes back.

How I verified it: import history since then.

### A placeholder movie with no year

Severity: low. Status: fixed 2026-11-04

What I found: Radarr had a movie with year 0 and an "announced" status.

Why it mattered: it could never be found or downloaded.

What I changed: I removed it.

How I verified it: it was gone.

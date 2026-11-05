# adguard: closed findings

Findings from the October and November 2026 audit of the lab's DNS that are fixed or
accepted. Each fix was re-verified on the live system before it was closed.
How the audit worked is in [METHODOLOGY.md](../METHODOLOGY.md), and the
current state is in [systems/adguard.md](../systems/adguard.md).

## High

### The DNS admin login was on the internet

Severity: high. Status: fixed 2026-10-17

What I found: the AdGuard Home admin login was published through the
Cloudflare Tunnel and Traefik, with only the AdGuard password in front of
it. Traefik's last hop to the Pi was plain HTTP, so the login crossed the
LAN unencrypted. On the LAN itself the UI also accepted logins over plain
HTTP. Because every request through the tunnel arrived from the same proxy
address, AdGuard's login lockout applied to all remote users at once, so a
stranger's failed attempts could lock me out. A DoH route on the same
hostname was dead and returned 404.

Why it mattered: anyone who got into the admin UI could redirect DNS for
every device in the house.

What I changed: I moved to a home-only design. I removed every AdGuard route
from Traefik, put Cloudflare Access in front of the hostname, and turned on
force HTTPS. A local rewrite now answers the resolver's hostname with
apollo's LAN address, so encrypted DNS and the admin UI work on the LAN with
a valid certificate.

How I verified it: Traefik listed no AdGuard routers, and the public
hostname returned a 404 from Traefik behind Access. Plain HTTP to the UI
redirected to HTTPS. From a LAN client, the hostname resolved to apollo,
DNS-over-TLS negotiated TLS 1.3 with a verified Let's Encrypt certificate,
and DNS-over-HTTPS answered.

### A DNS-edit API token on the Pi

Severity: high. Status: accepted 2026-10-17

What I found: apollo renews its certificate with a DNS-01 challenge, so it
holds a Cloudflare API token that can edit DNS records for my domain. The
token was in a world-readable file.

Why it mattered: anyone with a shell on the Pi could change the public DNS
for the domain.

Why I accepted it: the token has to be able to edit DNS for the challenge to
work. I confirmed in the Cloudflare dashboard that its scope is DNS edit on
that one zone only, and I restricted the file to its owner. Delegating the
challenge record to a separate zone would narrow it further, but it needs a
second domain, which I decided is not worth it for now.

How I verified it: the file's permissions were re-checked as owner-only. The
token's scope can only be seen in the Cloudflare dashboard, so that part is
reported by me.

### An OS that had never been updated

Severity: high. Status: fixed 2026-10-20

What I found: apollo's OS had not been upgraded since it was installed a
year earlier. 363 updates were pending against package lists six months
old, including security updates, and unattended-upgrades was not installed.

Why it mattered: the DNS server for the whole network was running a year of
unpatched packages.

What I changed: I ran a full upgrade, then installed and enabled
unattended-upgrades for the Debian, Debian security and Raspberry Pi
repositories.

How I verified it: the apt history showed 509 packages upgraded and nothing
left pending. unattended-upgrades was enabled and active with the expected
repositories, and its configuration parsed cleanly in a dry run.

### No copy of the config off the Pi

Severity: high. Status: fixed 2026-11-05

What I found: the only copy of AdGuard's config and the certificate setup was
the updater's backup on the same SD card.

Why it mattered: a failed SD card would have meant rebuilding every list,
rule, local name and setting from memory.

What I changed: kronos now pulls the config and the certificate files every
night, with a key that can only run that one export, and keeps them in its
snapshots and in B2.

How I verified it: the nightly copy was in a ZFS snapshot and in the B2
snapshot, and I restored it into a temporary AdGuard container that came up
working.

### Bad power and an SD card

Severity: high. Status: fixed 2026-11-05

What I found: the Pi logged undervoltage and throttling twice within 35
minutes of booting, on a stand-in power supply. The OS, config and query log
all live on one SD card, which bad power can corrupt, and the journal was
kept only in memory, so earlier faults left no trace.

Why it mattered: the primary resolver for the whole house was running on
power that could corrupt its only disk.

What I changed: I fitted the official power supply, and kept the journal on
disk with a size cap.

How I verified it: after almost two days up, the Pi reported no throttling
and no undervoltage, and the journal was writing to disk.

## Medium

### One resolver, and a silent fallback

Severity: medium. Status: fixed 2026-10-20

What I found: apollo was the only filtering resolver, with one upstream and
no fallback. DHCP handed out a public resolver as the second DNS server, so
when apollo was down, clients quietly switched to it and lost filtering.
That had already happened: apollo had been off for about six months, and
nothing noticed, because DNS kept working. Nothing alerted when apollo
stopped answering.

Why it mattered: the network looked healthy while ad and threat blocking was
off for every device, and the same fallback let any client skip filtering
whenever it liked.

What I changed:

- Added a second AdGuard Home, artemis, as a container on poseidon (see
  [decision 0007](../decisions/0007-second-adguard-on-poseidon.md)), with
  adguardhome-sync copying apollo's config to it every 15 minutes.
- Added a check on poseidon that alerts in Discord when either resolver or
  the sync has a problem.
- Changed DHCP on every network to hand out apollo and artemis only.
- Added Cloudflare as a second upstream next to Quad9.

How I verified it: the two configs matched field by field, apart from the
expected differences such as TLS and install paths. Both resolvers gave the
same answers for normal, blocked and local names. The check posted an alert
and a "resolved" message in a test. Every network's DHCP settings listed only
the two resolvers.

### Three months of everyone's DNS history

Severity: medium. Status: fixed 2026-10-18

What I found: the query log kept 90 days of every lookup from every client,
with client addresses, and had grown to 1.64 GB on the Pi. Statistics, which
are small, kept only 1 day.

Why it mattered: it was a detailed browsing history for every device on the
network, and a lot of writes on the Pi's storage.

What I changed: I cut query log retention to 7 days and raised statistics
retention to 7 days.

How I verified it: the AdGuard config showed 7 days for both.

### One rate limit shared by a whole network

Severity: medium. Status: fixed 2026-10-18

What I found: the rate limit was 30 queries per second per /24, so every
client on the Trusted network shared one budget.

Why it mattered: one busy device could get DNS throttled for every other
device on its network.

What I changed: I set the limit to apply per client address, at 32 queries
per second.

How I verified it: the AdGuard config showed the /32 subnet length and the
new limit.

### Passwordless sudo on the resolver

Severity: medium. Status: accepted 2026-11-05

What I found: my account has passwordless sudo, so any key that can log in as
me is effectively root. AdGuard runs as root and updates its own binary.

Why it mattered: whoever gets into my account controls the house's DNS.

What I changed (or why I accepted it): I kept it, the same as on the backup
host. The nightly config export uses its own narrow rule, which allows only
that one command.

How I verified it: the export rule is still the only narrow rule, and the
nightly export runs.

## Low

### A stale certificate config on the live path

Severity: low. Status: fixed 2026-10-18

What I found: acme.sh had a second certificate config for a placeholder
domain that could never validate. It pointed at the same file path as the
live certificate.

Why it mattered: it was dead config pointing at the live certificate, so it
could only get in the way of renewals.

What I changed: I removed the placeholder config.

How I verified it: acme.sh listed only the real certificate, with its next
renewal date, and the placeholder's folder was gone.

### A filter list from a third-party host

Severity: low. Status: fixed 2026-10-20

What I found: one of the enabled filter lists, a paywall-bypass list, was
fetched from a third-party Git host rather than from the list's usual
sources.

Why it mattered: whoever controls a filter list decides which domains every
client can and cannot resolve. A compromised list could block or allow
anything.

What I changed: I removed the list. It does little on its own without
browser add-ons.

How I verified it: a later read of the config no longer listed it.

### Bootstrap DNS from a single provider

Severity: low. Status: fixed 2026-10-20

What I found: after adding Cloudflare as a second upstream, all of the
bootstrap servers, which AdGuard uses to look up the DoH upstreams'
hostnames, were still Quad9.

Why it mattered: during a full Quad9 outage, AdGuard could not look up
Cloudflare's DoH hostname once its cached address expired, so both upstreams
could fail together.

What I changed: I added Cloudflare's addresses to the bootstrap list on
apollo. The sync copied them to artemis.

How I verified it: both configs listed the Quad9 and Cloudflare bootstrap
addresses after the next sync, which ran without errors, and both resolvers
answered normally.

### apollo's switch port was not recorded

Severity: low. Status: fixed 2026-10-17

What I found: apollo was offline when the network topology was collected,
so the docs did not say which switch port it used.

Why it mattered: the port is needed to trace a cabling or VLAN problem.

What I changed: I re-collected the topology once apollo was back.

How I verified it: the gateway showed apollo on its switch port, on the
Services network at 1 Gbps.

### Local names didn't resolve both ways

Severity: low. Status: fixed 2026-11-05

What I found: reverse lookups for LAN addresses had nowhere to go, so the
query log showed bare addresses. The networks also used three different local
domains, none of them matching AdGuard's own `.lan` names.

Why it mattered: logs and tools that look up names from addresses showed
nothing useful.

What I changed: AdGuard sends reverse lookups for private addresses to the
gateway, and every network now hands out `lan` as its domain.

How I verified it: both resolvers named a test host and the gateway, and the
gateway's settings showed `lan` on all five networks.

### Restore never tested

Severity: low. Status: fixed 2026-11-05

What I found: none of the DNS runbooks had been tested.

Why it mattered: the restore I would need after an SD card failure had never
been tried.

What I changed: I restored the nightly copy from a backup snapshot into a
temporary container on poseidon, reachable only from that host, and updated
the runbook to use that copy.

How I verified it: the restored resolver answered queries, blocked a known
tracker, returned the local names, served the certificate and required a
login.

### New kernels never booted

Severity: low. Status: fixed 2026-11-03

What I found: Raspberry Pi kernel packages don't flag that a reboot is
needed, so unattended-upgrades installed a new kernel while the old one kept
running.

Why it mattered: kernel security fixes were installed but not in effect.

What I changed: I rebooted onto the new kernel, and I reboot by hand after
kernel updates.

How I verified it: the running kernel matched the installed one.

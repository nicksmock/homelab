# network: closed findings

Findings from the October and November 2026 audit of the network that are fixed or
accepted. The audit used a local, read-only UniFi account, so some settings
could not be read. Where a write-up relies on what I saw in the UniFi UI
rather than on what the audit read, it says so. How the audit worked is in
[METHODOLOGY.md](../METHODOLOGY.md), and the network's current state is in
[systems/network.md](../systems/network.md).

## High

### VPN clients can reach every zone

Severity: high. Status: accepted 2026-10-19

What I found: the VPN zone used the predefined policies, which allow VPN
clients to start connections to every zone, including Management. The VPN
was in active use, with about 654,000 policy hits from VPN into the internal
networks. The read-only account could not list who has VPN access.

Why it mattered: anyone holding a VPN login has the same reach as an admin
device plugged into the LAN, including the management addresses of the
network gear.

Why I accepted it: the VPN is how I troubleshoot from outside, so it needs
to reach everything, Management included. Only my own account has VPN
access. That makes the account as powerful as a LAN admin device, so it
keeps its passkey and two-factor sign-in.

How I verified it: the policy table read by the audit showed the allow-all
VPN rules. VPN access being limited to my account is from my review in the
UniFi UI, and matches the admin account review below.

## Medium

### Intrusion detection that blocked nothing

Severity: medium. Status: fixed 2026-10-17

What I found: the intrusion system was enabled on all five networks with 33
rule categories, but it ran in IDS mode. In that mode it only raises alerts,
so none of those categories blocked any traffic.

Why it mattered: LAN devices could still reach known command-and-control,
compromised and malicious hosts, with only an alert to show for it.

What I changed: I switched the mode from IDS to IPS, so matching traffic is
blocked as well as logged.

How I verified it: the gateway settings showed mode `ips` with the same 33
categories enabled. WAN throughput was unchanged afterwards.

### Admin accounts the audit could not see

Severity: medium. Status: accepted 2026-10-17

What I found: the read-only role could not read admin accounts, device SSH
settings, VPN users or the cloud remote-management state. The admin list
endpoint returned 404, so that part of the gateway was unaudited.

Why it mattered: admin accounts and SSH are the main ways to take over the
network, and nothing in the audit data covered them.

Why I accepted it: I reviewed them in the UniFi UI instead. There are three
accounts: my cloud account, which signs in with a passkey, a local admin
account kept as break-glass access for when the cloud is unreachable, and the
local read-only account the audit used. SSH on the switch and APs accepts
keys only.

How I verified it: this one rests on my review in the UI. The read-only
account confirmed only what it could see of itself: local-only, with
read-only permissions.

### Unattended nightly updates

Severity: medium. Status: accepted 2026-10-17

What I found: the console firmware and every UniFi device update
automatically each night at 03:00.

Why it mattered: a bad release can take down the network, and with it the
Cloudflare Tunnel and the alerts that would report the outage, while nobody
is watching.

Why I accepted it: this is a home lab, not a production environment, so a
bad update worries me less here than it would at work. I kept nightly
automatic updates on the release channel.

How I verified it: the site settings still showed the 03:00 update schedule
and device auto-upgrade on in a re-check the same evening.

### Recovery secrets

Severity: medium. Status: accepted 2026-10-17

What I found: the read-only role cannot read Wi-Fi passphrases, so they were
not part of the documentation set. It was also unknown whether the two-factor
recovery codes for my UniFi cloud account were stored anywhere. Getting back
into the console after a lockout depends on that account.

Why it mattered: the network can be rebuilt from the docs, but not without
the Wi-Fi passphrases, and not at all if the admin account is lost.

Why I accepted it: the Wi-Fi passphrases are now stored with the lab's other
secrets, and the local break-glass admin gives a second way in. The recovery
codes are kept in my password manager rather than offline, which I accepted.

How I verified it: the presence of the passphrase entries was checked
without reading their values. The rest is reported by me.

### Gateway backups I couldn't see

Severity: medium. Status: accepted 2026-11-05

What I found: the console's automatic backup was on and the network app's own
backup was off, and the read-only account couldn't see the schedule, how long
backups are kept, or where they go.

Why it mattered: the gateway holds every network, firewall and Wi-Fi setting,
and a failed console with no usable backup means rebuilding all of it.

What I changed (or why I accepted it): I checked in my UniFi account: system
backups run weekly and before major updates, and 21 are listed, the newest
from that morning. Ubiquiti's docs say the system backup covers the whole
console, so the separate network-only backup isn't needed on a Cloud Gateway.
Ubiquiti doesn't publish how long cloud backups are kept, which I accepted.

How I verified it: by checking the backup list in my account.

## Low

### Addressing drift

Severity: low. Status: fixed 2026-10-18

What I found:

- The UniFi devices took their management addresses from DHCP, from a pool
  covering almost the whole Management subnet, with no reservations.
- Half of the DHCP reservations were tied to randomized private Wi-Fi MAC
  addresses, which can change and silently break the reservation.
- Two reservations pointed at devices that no longer used them.
- Some clients carried disabled fixed addresses from an older layout.
- The Management network was misspelled.

Why it mattered: the addresses of the network gear could change, and the
reservation list no longer described the network.

What I changed: I gave the UniFi devices static addresses, shrank the
Management pool to 10.0.1.100 to 10.0.1.200, removed the stale and
randomized-MAC reservations, keeping only those for infrastructure, and
renamed the network to Management.

How I verified it: a re-collection showed the static device addresses, the
new pool, the shorter reservation list and the corrected name. About 25 old
client records from rotating MAC addresses are still in the controller's
known-client list. They no longer show in the UI and do nothing, so I left
them.

### Bufferbloat and an unused second WAN

Severity: low. Status: fixed 2026-10-18

What I found: Smart Queues were off on a connection with a small upload, so
latency was likely to spike whenever the upload was busy. A second WAN was
configured for failover, but nothing was plugged into it.

Why it mattered: a saturated upload would have slowed everything else on the
connection.

What I changed: I ran a bufferbloat test, which graded the connection C, then
turned on Smart Queues. The retest graded B. The second WAN had no port assigned, so there was nothing to
remove.

How I verified it: a re-collection showed Smart Queues on for the WAN with
the new limits. The test grades are from my own runs.

### Two hardware addresses for one server

Severity: low. Status: accepted 2026-11-05

What I found: the gateway listed two hardware addresses for poseidon's IP,
along with two smaller poseidon settings that were already fixed on the
server.

Why it mattered: client lists and reservations can follow the wrong address.

What I changed (or why I accepted it): the second address comes from a Docker
setting that poseidon needs to reach the second DNS resolver, so I kept it.
Details are in the [poseidon findings](poseidon.md#two-hardware-addresses-for-one-ip).

How I verified it: the server's reservation and both resolvers work.

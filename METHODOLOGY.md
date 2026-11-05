# Methodology

How I audited the lab in October 2026, and how these docs are kept true.

## Scope and phases

The lab is split into four systems: poseidon (the Unraid server), network
(the UniFi gateway, switching and Wi-Fi), adguard (the Raspberry Pi DNS
server) and cloudflare (the DNS zone, tunnel and Access). Each system was
documented in phases, one at a time, and each phase was reviewed before the
next one started. For poseidon the phases were:

1. Inventory: hardware, OS, plugins, array and pools, disk health, shares,
   schedules, notifications.
2. Containers: images, networks, mounts, users and privileges, GPU use, how
   media and download paths are laid out.
3. Network: interfaces, Docker networks, firewall, listeners, reverse proxy
   routes, and what is reachable from where.
4. Audit: every finding from the first three phases, consolidated and
   prioritized.
5. Runbooks: rebuild, disk replacement, flash drive failure, appdata restore.

The other systems followed the same pattern, with phases that fit them.

## Read-only collection

- Collection never changed anything on a system. No writes, restarts, moves,
  deletes or config changes. For each system I wrote down the access method
  and a list of commands that were forbidden outright, such as container
  control, array and parity commands, plugin changes and anything that writes
  to the Unraid flash drive. If the effect of a command was unclear, it was
  not run until I had decided.
- Disk health was read with `smartctl -n standby`, so sleeping disks were
  skipped rather than spun up.
- API-based systems used read-only, narrowly scoped credentials: a custom
  read-only role on the UniFi gateway and a read-only Cloudflare API token.
  If only an admin credential had existed, the rule was
  to say so, use it only for read calls, and record it as a finding.
- On the Linux hosts, read-only was a rule rather than a permission. It was
  enforced by the forbidden-command lists and by my review of what was run.
- When a change was needed, it went into the audit as a recommendation. I
  made every change myself.

## Nothing recorded until observed live

Existing docs and other systems could point to where to look. For example, the
gateway reported which IP the DNS server should have. But nothing was written
down as fact about a system until it had been observed on that system. Where
something could not be determined, the docs say so instead of guessing.

A few things cannot be seen with read-only access, such as a setting only
visible in an admin UI. When I checked those myself, the private docs mark
them as reported by me rather than observed.

## Findings in one place

Each phase doc ends with the findings from that phase, with a severity (high,
medium or low) and a one-line recommendation. Those tables are a record of
what was found on the collection date.

The audit phase merges them into one list per system. Related findings
become a single item, and the severity is re-rated where the combination is
worse than the parts. For example, a finding about where Unraid sent its
alerts and one about a monitoring script that could not see a disabled disk
became one item: a failed disk that no one was told about. Each item lists
the phase findings it came from, plus an effort estimate.

Each system's audit doc is the only place where a finding's status is kept:

- `open`: not addressed yet.
- `fixed YYYY-MM-DD`: the fix was re-verified on the live system.
- `accepted YYYY-MM-DD`: I chose to keep it as is, with the reason written
  down.

A finding is never deleted. Its status changes. Findings raised later, for
example while writing runbooks or during a re-check, are added to the audit
doc with their source.

## Re-verification before closing

When I make a change, it is not marked fixed on my word. The affected data is
re-collected from the live system, read-only, the phase doc is updated with
the new collection date, and only then does the finding's status change. The
earlier output is kept next to the new output.

Some examples from poseidon:

- After switching SSH to key-only, the running SSH config was read and a
  password-only login was tried and refused.
- After replacing a failed disk, the fix was closed only once the rebuild
  completed and a full non-correcting parity check finished with 0 errors.
- The replacement monitoring script was compared with the reviewed copy, and
  it was closed only after it detected the real disabled disk and its alert
  arrived in Discord.

Where part of a fix cannot be seen from the system, such as revoking an API
key in a provider's console, the finding says which part was verified and
which part was reported by me.

The findings write-ups in [findings/](findings/) cover only items that are
fixed or accepted.

## Secrets and raw output

- Secret values never go into the docs. API keys, tokens, passwords, webhook
  URLs and license keys are written as named placeholders. Real values are kept in a separate secrets file that
  is not committed, with a matching example file of dummy values so the names
  stay documented.
- Full command output is saved unedited, but only in the private working repo.
  It is treated as being as sensitive as the secrets file, because container
  environments and config dumps contain keys and identifiers. It is never
  copied, quoted or uploaded anywhere else.
- The working docs hold curated content only. Before a doc is finished it is
  searched for likely leaks, such as long hex or base64 strings, webhook URLs
  and password fields.

## Private working docs and this repo

The audit lives in a private repo. This public repo is derived from it, and
content only flows one way. Every fact here comes from the private docs' current
verified state. Open findings stay private until they are closed, and these
docs are written so they do not reveal them.

Before anything is committed here, a leak check runs. It looks for MAC
addresses, UUIDs, email addresses, long tokens, credential words, public IP
addresses, any of the real secret values, and a private denylist of names,
serials and IDs.

## How AI was used

I did this audit with Claude, an AI assistant, working under written rules
that I set for each system and for the project as a whole.

- Claude ran the read-only collection over SSH and the read-only APIs, saved
  the raw output, and drafted the phase docs, the audit and the runbooks.
- I reviewed every doc. I made every change to the lab myself. Claude's role
  after a change was to re-collect the data and re-verify it under the rules
  above.
- Claude also drafted the docs in this repo, under a separate set of
  publishing rules. I reviewed each one before it was published.
- Rationale for design decisions comes from me. Where the reason for a choice
  was not written down, Claude asked rather than supplying one.

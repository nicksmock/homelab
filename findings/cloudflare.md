# cloudflare: closed findings

Findings from the October and November 2026 audit of the Cloudflare account that are
fixed or accepted. The audit read the account with a read-only API token, so
billing and other API tokens were out of its sight. Where a write-up relies
on what I saw in the dashboard, it says so. How the audit worked is in
[METHODOLOGY.md](../METHODOLOGY.md), and the current state is in
[systems/cloudflare.md](../systems/cloudflare.md).

## High

### An Access policy that let in any GitHub user

Severity: high. Status: fixed 2026-10-17

What I found: the account's only Access policy was reusable, and its include
rule was "login method is GitHub". That admits anyone with a GitHub account,
not just me: it checks that a person signed in, but not who they are. It
guarded a single hostname that no longer had a service behind it.

Why it mattered: the policy looked like protection. Attaching it to a real
app, such as the DNS admin UI, would have made that app open to every
GitHub user in the world.

What I changed: I deleted the stale application and its policy. I created a
new reusable policy that allows only my own identities by name, and attached
it to a new Access application for the DNS admin hostname, with GitHub as
the login method.

How I verified it: the API no longer listed the old application or policy.
It showed the new application on the DNS admin hostname, using the new
policy. I signed in through it to confirm the login works.

### Every hostname went through the tunnel

Severity: high. Status: fixed 2026-11-05

What I found: the domain had a wildcard DNS record and a wildcard tunnel
rule, both pointing at Traefik. Any new Traefik route was public at once, and
five stale records for services I had removed still led to Traefik.

Why it mattered: a route meant for the LAN only would have been published to
the internet without anyone deciding to publish it.

What I changed: I deleted the stale records, then added an explicit public
hostname in the tunnel for each app I want reachable, and removed the
wildcard from the tunnel and DNS
([decision 0013](../decisions/0013-explicit-tunnel-hostnames.md)). The apps
stay behind their own logins.

How I verified it: each published app answered as before through its own
route, and a made-up hostname no longer resolved.

## Medium

### No alerts from Cloudflare

Severity: medium. Status: fixed 2026-10-17

What I found: the account had no notification policies. A tunnel outage, a
certificate problem or a DDoS event would have told no one.

Why it mattered: remote access to the lab depends on the tunnel, and
elsewhere in the lab silent failures had already gone unnoticed for weeks.

What I changed: I added a tunnel health notification that emails me when
the tunnel is degraded or down.

How I verified it: the API listed the notification policy, scoped to the
tunnel, for the degraded and down states, with email delivery.

### The weakest SSL/TLS mode

Severity: medium. Status: fixed 2026-10-17

What I found: the zone's SSL/TLS encryption mode was Flexible, the weakest
setting, in which Cloudflare talks to an origin over plain HTTP. The origin
already had a Cloudflare Origin CA certificate, which is what Full (strict)
is meant to verify. Today's traffic goes through the tunnel, so the setting
probably had no effect yet, but it would have applied to any proxied record
added later with an IP origin.

Why it mattered: a future record could have sent traffic to an origin
unencrypted, with nothing to warn me.

What I changed: I set the mode to Full (strict).

How I verified it: the zone setting read `strict`, and every public app
still answered normally afterwards.

### No mail or CA records for a domain that sends no mail

Severity: medium. Status: fixed 2026-10-17

What I found: the domain sends and receives no mail, but nothing in DNS said
so. There was no MX, SPF or DMARC record, so receivers had no instruction to
reject mail spoofing the domain. There were also no CAA records, so any
certificate authority could issue for it.

Why it mattered: anyone could send convincing mail from the domain, and a
mis-issued certificate from any CA would have been valid.

What I changed: I added a null MX, `v=spf1 -all`, and DMARC with
`p=reject` and strict alignment. I added CAA records for Let's Encrypt,
which the LAN resolver uses, and for the CAs Cloudflare uses for edge
certificates.

How I verified it: the records were checked in the API and through public
resolvers. The first null MX was created at the wrong name, and that check
caught it. I corrected it and re-checked. After the CAA change, every edge
certificate was still active, and the CAA set Cloudflare publishes still
allows its own CAs to renew them.

### A tunnel token in old copies

Severity: medium. Status: fixed 2026-11-04

What I found: the tunnel's token sat in two old container templates as well
as the live one, and in past backups. I also couldn't see from the read-only
audit token whether the Pi's DNS-edit token was scoped the way I believed.

Why it mattered: anyone with the tunnel token can run a connector for the
tunnel and take its traffic.

What I changed: I rotated the tunnel token and deleted the two old templates.
Old copies in backups age out on their own. I didn't reissue the origin
certificate: nothing else uses it, and its key is now readable only by its
owner.

How I verified it: the running connector used the new token, opened fresh
connections with no authentication errors, and the published apps answered.

### Video through the tunnel

Severity: medium. Status: accepted 2026-11-04

What I found: the media server streamed video through Cloudflare's proxy and
tunnel, with default caching.

Why it mattered: Cloudflare's terms restrict serving video through its CDN,
and the tunnel goes through it.

What I changed (or why I accepted it): remote streaming is rare, for family
on tablets, and I didn't want them to need a VPN. I added a rule that turns
off caching for the media server's hostname and accepted the remaining risk.

How I verified it: the rule was in place, and a file from that hostname came
back marked as not cached.

## Low

### Account settings left at defaults

Severity: low. Status: accepted 2026-10-17

What I found: the audit flagged four account settings:

- Third-party OAuth app access was on.
- Two-factor enforcement for members was off. The only member, me, has it
  on.
- Domain auto-renew depends on a payment method the read-only token cannot
  see.
- An advanced certificate pack, normally a paid add-on, sat alongside the
  free certificate.

Why it mattered: each one is either a door left open for a future member or
integration, or a cost and renewal risk the audit could not check.

Why I accepted it: OAuth app access stays on because the GitHub sign-in uses
it. I will turn on two-factor enforcement before adding any other member.
Billing is current, and the advanced certificate pack is not billed.

How I verified it: the settings are as recorded by the API. The billing
details are from my own check in the dashboard.

### A documentation token with an expiry date

Severity: low. Status: fixed 2026-10-17

What I found: the read-only token the audit uses was set to expire about
six weeks after it was created.

Why it mattered: every later re-check would have failed after that date, so
the docs would have quietly stopped being verified.

What I changed: I removed the expiry. The token stays read-only.

How I verified it: the token verify endpoint showed it active with no
expiry.

### A DNSSEC change with no recorded cause

Severity: low. Status: accepted 2026-10-17

What I found: DNSSEC had been modified ten days before the audit, and
nothing visible to the audit explained why.

Why it mattered: an unexplained change to DNSSEC can be a sign of someone
else in the account, or can break resolution for the whole domain.

Why I accepted it: I had enabled DNSSEC deliberately. It is active with the
DS record published, so no change was needed.

How I verified it: the API showed DNSSEC active with the DS record
published. That the change was mine is reported by me.

### No limits on login attempts

Severity: low. Status: fixed 2026-11-04

What I found: there were no custom WAF or rate-limiting rules, so nothing at
the edge slowed down repeated login attempts.

Why it mattered: at that point CrowdSec could not tell visitors apart, so the
edge was the only place a per-client limit could work.

What I changed: I added a rate-limiting rule on the apps' login paths, and
had already blocked AI crawlers at the edge. I kept Bot Fight Mode off,
because it can break the mobile apps.

How I verified it: the rule read back through the API as deployed, and a
normal login from a phone outside the home network still worked.

### Query strings in the apex page's logs

Severity: low. Status: accepted 2026-11-04

What I found: the domain's apex is served by a small Worker, and its logs keep
full request URLs, including query strings.

Why it mattered: logs can hold anything a client puts in a URL.

What I changed (or why I accepted it): the Worker serves a static page, the
logs stay in my account and aren't exported, and the dashboard offers no
setting to redact them.

How I verified it: logging is on, export is off, and redaction is off.

### Runbooks never rehearsed

Severity: low. Status: fixed 2026-11-05

What I found: none of the Cloudflare runbooks had been tested.

Why it mattered: the emergency shut-off is the one I would need under
pressure.

What I changed: I rehearsed it by stopping the tunnel's connector, and
updated the step that cuts single hostnames now that there is no wildcard.

How I verified it: every published app returned Cloudflare's tunnel error
within seconds and the tunnel showed as down. Starting the connector brought
it back with all apps answering.

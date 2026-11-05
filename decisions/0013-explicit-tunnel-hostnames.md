# 0013: Explicit tunnel hostnames instead of a wildcard
Status: accepted

## Context

The tunnel and DNS used a wildcard for the domain. Every hostname went to
Traefik, so any Traefik route was public as soon as it existed.

## Decision

Each app that should be reachable from the internet gets its own public
hostname in the tunnel, which also creates its DNS record. There is no
wildcard. I want new routes to stay private unless I publish them on purpose.

## Alternatives considered

- Keeping the wildcard and relying on Traefik routes alone.
- Keeping the wildcard and putting Cloudflare Access in front of everything.

## Consequences

- Publishing a new app is two steps: a Traefik route, and a public hostname
  in the tunnel.
- A hostname that isn't listed doesn't resolve.
- The emergency shut-off can cut one app at a time by deleting its hostname.

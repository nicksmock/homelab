# 0015: CrowdSec's Traefik plugin instead of a standalone bouncer
Status: accepted

## Context

CrowdSec decides which addresses to ban from Traefik's access log. A
separate bouncer container enforced those bans for Traefik through forward
auth. The bouncer image I used had not been updated in about three years.

## Decision

I replaced the bouncer container with the maintained CrowdSec plugin that
runs inside Traefik, as the same middleware name, so no route had to change.

## Alternatives considered

- Keeping the old bouncer container.

## Consequences

- One fewer container. Traefik downloads the plugin when it starts.
- The plugin uses its own CrowdSec API key, kept in a file Traefik reads.
- A test ban returned 403 for that address on the published apps.

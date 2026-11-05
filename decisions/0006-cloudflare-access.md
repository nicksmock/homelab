# 0006: Cloudflare Access instead of Tinyauth
Status: accepted

## Context

I had been using Tinyauth, a self-hosted forward-auth service, as a Traefik
middleware to put a login in front of some routes.

## Decision

Where a hostname needs a login before traffic reaches the lab, I use
Cloudflare Access instead. I removed Tinyauth on 2026-10-17.

I switched because the Tinyauth middleware did not work on some important
containers. Those containers have since been removed.

## Alternatives considered

- Tinyauth as a Traefik middleware, which I used before.

## Consequences

- The login check happens at Cloudflare's edge, before a request enters the
  tunnel.
- Access policies are managed in Cloudflare, not in Traefik.
- One fewer service to run and keep updated on poseidon.

## Update, November 2026

No hostname needs Access right now. The DNS admin UI is no longer published
at all, and the apps that are published use their own logins. Since
[decision 0013](0013-explicit-tunnel-hostnames.md), a hostname is only public
if I add it to the tunnel. If an admin UI ever has to be reachable from
outside, Access is still the way I would protect it.

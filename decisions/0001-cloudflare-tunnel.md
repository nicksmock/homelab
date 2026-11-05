# 0001: Cloudflare Tunnel for remote access instead of port forwards
Status: accepted

## Context

A few web apps on poseidon need to be reachable from outside the home
network. The usual way to do that is to forward ports on the gateway to the
server.

## Decision

Remote access goes through a Cloudflare Tunnel. A cloudflared container on
poseidon opens the tunnel outbound to Cloudflare and hands requests to
Traefik, which routes them to containers. The gateway has no port forwards.

I chose the tunnel because it seemed safer than port forwarding.

## Alternatives considered

- Port forwarding on the gateway to a reverse proxy on poseidon.

## Consequences

- The gateway has no port forwards to the server, and UPnP is off on the
  server.
- Public hostnames, DNS records and Access policies live in Cloudflare, not
  on the server.
- Remote access depends on Cloudflare and on the cloudflared container. A
  Cloudflare tunnel health alert reports when the tunnel goes down.

See [systems/poseidon.md](../systems/poseidon.md) for how the path works.

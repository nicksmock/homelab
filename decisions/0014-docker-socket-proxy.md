# 0014: A socket proxy between Traefik and Docker
Status: accepted

## Context

Traefik builds its routes from container labels, which it reads from the
Docker API. It had the Docker socket mounted. A read-only mount doesn't limit
what the API allows, so control of Traefik meant control of every container
and the host. Traefik is also the container that handles traffic from the
internet.

## Decision

Traefik reads the Docker API through a socket proxy instead of the socket.
The proxy runs unprivileged, read-only, with no published ports. It answers
only the Traefik container, and only the read requests Traefik's Docker
provider makes.

## Alternatives considered

- A proxy that filters by request type but answers any container. All my
  containers share one network, so any of them could have read every
  container's settings, including secrets in their environment.
- Defining Traefik's routes in files, with no Docker access at all.

## Consequences

- One more container. If it is down, Traefik keeps its last routes but can't
  pick up changes.
- Rebuilding Traefik means keeping its Docker endpoint pointed at the proxy,
  with no socket mount.

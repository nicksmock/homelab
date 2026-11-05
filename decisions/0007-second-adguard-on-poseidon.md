# 0007: Second AdGuard Home as a container on poseidon, on macvlan
Status: accepted

## Context

The lab's DNS filtering ran on one AdGuard Home instance, on apollo, a
Raspberry Pi at 10.0.20.5. Clients had a public resolver as their second DNS
server, so whenever apollo was down they lost filtering without anyone
noticing.

## Decision

A second AdGuard Home, artemis, runs as a container on poseidon. It has its
own LAN address, 10.0.20.6, on a macvlan Docker network. An adguardhome-sync
container copies apollo's configuration to artemis every 15 minutes. DHCP
on every LAN now hands out apollo and artemis, and no public resolver.

I put it on poseidon because poseidon was available. macvlan was necessary
given the hardware. I tried ipvlan first, but had issues with containers on
it.

## Alternatives considered

- ipvlan for the container network (tried).

## Consequences

- Clients have two filtering resolvers. A public resolver is no longer
  handed out.
- Changes are made on apollo. artemis follows within 15 minutes.
- A scheduled script on poseidon checks both resolvers and the sync container
  every 5 minutes and alerts in Discord.
- One of the two resolvers now depends on poseidon being up.

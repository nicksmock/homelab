# 0009: DHCP reservation for poseidon instead of a static IP
Status: accepted

## Context

poseidon needs a stable address, 10.0.20.10. It can come from a static IP set
in Unraid, or from a DHCP reservation on the gateway.

## Decision

poseidon gets its address from a DHCP reservation on the gateway, with no
static IP set in Unraid.

I prefer reservations to static addresses. If the network stack dies and I
need to swap in a basic replacement router quickly, I don't have to change
subnetting on the server. It takes whatever the new router hands out.

## Alternatives considered

- A static IP set in Unraid.

## Consequences

- The address is managed in one place, the gateway.
- poseidon keeps 10.0.20.10 only while the gateway's reservation exists. A
  replacement router gives it a different address until a reservation is
  added there.

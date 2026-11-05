# Add a VLAN end to end

| Value | This lab |
|---|---|
| Gateway | Zeus, UniFi Cloud Gateway Max, zone-based firewall |
| Switching | UniFi switch and APs. Ports default to Management untagged with every other VLAN tagged |
| DNS to hand out | 10.0.20.5 and 10.0.20.6 (the two AdGuard Home resolvers) |
| Addressing pattern | `10.0.<VLAN>.0/24`, gateway `.1`, DHCP pool `.100` to `.200` |

Use this to add a network, or to bring an unused one into service, from the
gateway to a working Wi-Fi client.

## 1. Network

In the UniFi Network app, **Settings > Networks**:

1. Create the network: name, VLAN ID, subnet and gateway, DHCP pool and lease
   time, following the addressing pattern.
2. Set the DHCP DNS servers to the lab's resolvers, so the new network is
   filtered like the others.
3. Choose its firewall zone: an existing one, or a new custom zone if it
   needs its own rules.

## 2. Firewall

1. Review what the chosen zone can reach, and what can reach it.
2. If the network is isolated, add an allow rule for DNS (port 53) to the
   resolvers. Isolation blocks them otherwise, and clients fall back to
   whatever DNS they can reach.
3. Add any specific allows the devices need, for example a printer that
   Trusted clients use.
4. Decide whether the network may reach the gateway's management UI, and
   block it if not.

## 3. Switching

- UniFi ports on the default profile carry every VLAN, so uplinks and AP
  ports carry the new one automatically.
- Ports with an override carry only what they are set to. Add the VLAN to
  any of them that need it.
- Any switch in the path that UniFi does not manage needs the VLAN added by
  hand, tagged on its uplink and on every port that feeds an AP.

## 4. Wi-Fi

In **Settings > WiFi**:

1. Create the SSID, assign the new network, and choose the security mode and
   bands the devices support.
2. Broadcast it from the AP group.
3. Store the passphrase with your other secrets.

## 5. Test

With one device on each AP:

- It gets an address in the new subnet.
- DNS resolves through the lab's resolvers, and a blocked domain is blocked.
- It reaches the internet.
- It cannot reach the other internal networks unless a rule allows it.

## 6. Move devices

Move devices over one group at a time, update any DHCP reservations they
had, and update the network docs.

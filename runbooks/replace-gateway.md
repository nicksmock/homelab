# Replace or reset the UniFi gateway

| Value | This lab |
|---|---|
| Gateway | Zeus, UniFi Cloud Gateway Max |
| Managed devices | One UniFi switch, three UniFi APs |
| Backups | UniFi cloud backups, plus a downloaded `.unifi` console backup |
| Servers with DHCP reservations | poseidon (10.0.20.10) |

Use this when the gateway has failed, or after a factory reset.

## Before (if the old gateway still works)

1. Download fresh backups: the console backup (`.unifi`) from UniFi OS, and
   the Network application backup (`.unf`).
2. Note the modem model. Cable modems often bind to the first router MAC
   they see, so a new gateway may need a modem power cycle.

## Restore onto a new or reset gateway

1. Connect the new gateway's WAN port to the modem. Don't connect the LAN
   yet.
2. Power-cycle the modem, then power on the gateway.
3. Run setup in a browser or the UniFi app, and choose **Restore from
   backup**:
   - A cloud backup, by signing in with my UniFi account.
   - A downloaded `.unifi` file.
   - With only a `.unf`, finish a minimal setup first, then restore it in
     the Network application's backup settings.
4. Wait for the restore and reboot, then log in.
5. Reconnect the LAN.
6. The switch and APs should come back on their own, because the restore
   brings back the site and device credentials. If one stays
   "Disconnected" or "Adopting" after about 10 minutes, factory-reset it and
   adopt it again.
7. Check that the WAN has an address. If not, power-cycle the modem again.

## No backup: rebuild by hand

Set the console up fresh, then recreate the configuration from the docs in
this order:

1. Site settings: time zone and NTP, update schedule, UPnP off, IPS mode and
   categories, honeypots, geo-IP blocking.
2. Networks: names, VLAN IDs, subnets, DHCP pools and lease times, DNS
   servers, isolation.
3. DHCP reservations, servers first, so DNS and the servers keep their
   addresses.
4. Wi-Fi. This needs the passphrases. If they are lost, set new ones and
   rejoin every client.
5. Firewall zones and policies.
6. Remote access VPN.
7. Devices: factory-reset the switch and APs, adopt them, rename them, and
   re-apply any port overrides.
8. Smart Queues, with limits matched to the connection.
9. The read-only account used for documentation.

## After (either path)

1. From a Trusted client, check that it gets an address and that DNS
   resolves.
2. Check that the servers kept their addresses and that the apps published
   through the Cloudflare Tunnel load from outside the LAN.
3. Download a new backup.
4. Re-collect the network docs and compare them with the old ones.

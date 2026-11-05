# Take a DNS resolver down for maintenance

| Value | This lab |
|---|---|
| Primary resolver | apollo, 10.0.20.5, AdGuard Home on a Raspberry Pi |
| Replica | artemis, 10.0.20.6, AdGuard Home container on poseidon |
| Sync | adguardhome-sync on poseidon, apollo to artemis every 15 minutes |
| DHCP DNS on every network | 10.0.20.5 and 10.0.20.6 |
| DHCP lease time | 24 hours (IoT 12 hours) |

Use this before rebooting, upgrading or rebuilding either resolver, or the
host it runs on. Clients already have both resolvers from DHCP, so they keep
filtered DNS while one is down. They may see a short delay on the first
lookups while they move to the other resolver.

## Before

1. Check that the resolver staying up answers and filters:
   ```bash
   nslookup example.com <other-resolver>
   nslookup doubleclick.net <other-resolver>     # expect 0.0.0.0
   ```
2. Check that the local names resolve through it, for example
   `poseidon.lan`.
3. If the primary (apollo) is going down, make no config changes until it is
   back. Changes are made on the primary and copied to the replica, and the
   next sync would overwrite anything changed on the replica.

## During

- Taking poseidon down also takes the replica and the sync down. apollo
  carries DNS alone until poseidon is back.
- The DNS health check posts an alert while a resolver is down, and a
  "resolved" message when it is back. That is expected.

## After

1. Check that the resolver answers, filters and resolves the local names, as
   in "Before".
2. If it was the replica, wait for the next sync run, or start one, and check
   its log for errors.
3. If it was the primary, check that the sync ran cleanly on its next
   schedule.

## Longer outages

If one resolver will be down for days, clients still work, but every client
that tries the missing resolver first waits on it. To make the switch clean:

1. A day ahead, lower the DHCP lease time to 1 hour on each network, so
   clients pick up DNS changes quickly.
2. Remove the missing resolver from the DHCP DNS servers.
3. When it is back, restore both DNS servers and the normal lease times.

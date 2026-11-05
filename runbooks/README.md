# Runbooks

Procedures for the lab, written so the steps are reusable. Each one starts
with a table of the values specific to this lab.

| Runbook | Use when |
|---|---|
| [Replace an array disk](replace-array-disk.md) | Unraid has disabled a disk, or one is failing |
| [Restore one container](restore-container.md) | One app's config or database is broken |
| [Replace the Unraid flash drive](restore-unraid-flash.md) | The boot drive dies or will not boot |
| [DNS resolver maintenance](dns-resolver-maintenance.md) | Taking a resolver, or its host, down |
| [Replace a ZFS mirror disk](replace-zfs-mirror-disk.md) | A disk in kronos's pool has failed |
| [Add a VLAN](add-vlan.md) | Adding a network, or bringing an unused one into service |
| [Replace the gateway](replace-gateway.md) | The gateway has failed or been reset |
| [Protect a hostname with Access](protect-hostname-with-access.md) | Publishing something only I should reach |
| [Emergency shut-off](emergency-shutoff.md) | Something published through the tunnel is under attack |

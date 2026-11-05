# 0011: Usenet only, no torrent or debrid client
Status: accepted

## Context

Downloads came from two paths: NZBGet for usenet, and rdt-client, which
handed torrents to a debrid service. The TV and movie managers could use
either, through usenet and torrent indexers in Prowlarr.

## Decision

I retired rdt-client and removed the torrent indexers, so all downloads come
from usenet through NZBGet. rdt-client really hadn't proven useful.

## Alternatives considered

- Keeping both paths, with usenet preferred.

## Consequences

- One download client to run, update and back up.
- Prowlarr has usenet indexers only, and the TV and movie managers have one
  download client.
- The `torrents/` folder in the data tree is gone (see
  [decision 0004](0004-single-data-tree.md)).
- A release that never reaches usenet stays missing. I keep those titles
  monitored, so a later posting is picked up.

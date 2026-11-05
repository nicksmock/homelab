# 0012: Pullbox instead of Mylar3 for comics
Status: accepted

## Context

Mylar3 managed the comics library: it searched indexers for wanted issues,
sent them to the download client and imported them into the library that
Komga serves.

## Decision

I replaced Mylar3 with Pullbox. Mylar3 is clunky and feels outdated.

## Alternatives considered

- Keeping Mylar3.

## Consequences

- Pullbox searches the usenet indexers through Prowlarr and sends downloads
  to NZBGet, like the TV and movie managers.
- Pullbox imported the Mylar3 library. I removed the duplicate copies Mylar3
  had left in the library afterwards.
- Pullbox runs as a fixed non-root user, so its library folder is owned by
  that user, and it reads NZBGet's downloads through a shared group.
- It mounts only the comics library and its download folder, not the whole
  data tree.

# 0004: One /data tree for downloads and media
Status: accepted

## Context

The download clients write finished downloads, and the arr apps (Sonarr,
Radarr and the others) import them into the media libraries. If downloads
and libraries are on different mounts, every import is a full copy.

## Decision

Downloads and media live in one user share. The download clients and the
arr apps all mount the whole share at the same path, `/data`:

```
/data
  media/
  torrents/
  usenet/
```

I chose this layout for hardlinking with the arr apps.

## Alternatives considered

None recorded.

## Consequences

- Imports are hardlinks or atomic moves, not copies, so a finished download
  does not take up space twice.
- Every container that handles downloads or imports has to mount the whole
  tree at `/data`, not a subfolder, or it loses this.
- Read-only consumers such as Jellyfin can mount just `media/`.

## Update, November 2026

I retired the torrent clients, so downloads are usenet only and the
`torrents/` folder is gone. The TV and movie managers still import with a
move on the same filesystem.

The comics manager, Pullbox, is the one exception to mounting the whole tree.
It used to have read-write access to all of `/data`, which it doesn't need.
It now mounts only the comics library and its own download folder, at the
same paths it would see under `/data`. Its imports become a copy and a delete
across the two mounts, which is fine for comic files.

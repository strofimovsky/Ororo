# Changelog

## [4.1.5] - 2026-07-19

### Fixed
- Android now uses Ororo's muxed MPEG-TS HLS endpoint instead of separate fMP4 audio/video renditions, avoiding Kodi's 30-second demux initialization timeout while retaining adaptive quality.
- Direct MP4 playback remains available as a final fallback when adaptive HLS cannot start.

## [4.1.4] - 2026-07-19

### Fixed
- Android playback now tries the adaptive HLS stream first and automatically retries the direct MP4 when Kodi cannot open the HLS stream.

## [4.1.2] - 2026-05-08

### Fixed
- "Mark show/season watched" now covers never-played episodes: any episode missing from Kodi's `files` table is inserted with `playCount=1`. Previously only already-played episodes would toggle, which made the season-level action look broken on fresh shows.

## [4.1.1] - 2026-05-08

### Added
- "Mark show watched" / "Mark show unwatched" context menu entries on Favourites and Subscriptions
- "Mark season watched" / "Mark season unwatched" context menu entries on season rows
- "Reset watched state" entry in the TV Shows root — clears all Ororo playcounts

### Notes
- Mark-watched only affects episodes that have been played at least once (never-played episodes are not stored in Kodi's database and remain unaffected). This matches the "watched means you played it" semantic.

## [4.1.0] - 2026-05-08

### Added
- Unread-episode counter on shows and seasons in Favourites/Subscriptions, shown as `Show Name (N)` where N is the unwatched count
- Parallel show detail fetching (10 concurrent workers) for fast Favourites/Subscriptions loading

### Fixed
- Cache key hashing broken on Python 3 / Kodi 19+: `hashlib.md5().update(str(x))` threw silently, making every per-show API call a cache miss. Now encodes to UTF-8 bytes before hashing
- Favourites/Subscriptions scan that previously issued one sequential API call per show (hanging on large lists) now runs in parallel and leverages the repaired cache
- Watched-state detection now reads directly from Kodi's video database, correctly recognizing played plugin URLs even when the show isn't in Kodi's library

### Changed
- Counter suffix simplified from `(N new)` / `(X episodes)` to just `(N)`; suppressed when zero

## [4.0.2] - 2026-01-10

### Added
- Episode counts on shows and seasons in Favourites/Subscriptions
- Toggle Watched context menu option

### Fixed
- Removed repository dependency blocking installation
- Switched to Kodi native watched tracking
- Fixed metadata deprecation warnings

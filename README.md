# Ororo.tv Kodi Addon (community fork)

Kodi addon for streaming movies and TV shows from [Ororo.tv](https://ororo.tv).

This is an unofficial community fork of Ororo.tv's official Kodi addon. The official plugin was last released as **v4.0.1** (March 2021) and is no longer actively maintained on GitHub. This fork picks up from there with Kodi 19+ fixes and a few quality-of-life additions around watched-state tracking. See [CHANGELOG.md](CHANGELOG.md) for the full history; the "Changes vs. upstream" section below summarises what's different.

## Changes vs. upstream (v4.0.1)

### Bug fixes
- **Python 3 cache was silently broken.** `hashlib.md5().update(str(x))` throws `TypeError` on Python 3 (Kodi 19+), and the exception was swallowed. Every per-show API call missed the cache — on a Favourites list of 20 shows, this meant 20 back-to-back HTTP requests on every open. Fixed by encoding to UTF-8 bytes before hashing (`cache.py`). Clearing the addon's `cache.db` after upgrading is recommended.
- **Favourites/Subscriptions loading hung.** Addon used to fetch `/shows/{id}` sequentially per favourite to compute labels. With the cache fix in place, we also parallelised these fetches (10 concurrent workers) — opening Favourites on a large list is now near-instant after the first fill.

### New features
- **Unwatched episode counter.** Shows and seasons in Favourites/Subscriptions render as `Show Name (N)` where `N` is the count of unplayed episodes. Hidden when zero. Watched state is read directly from Kodi's `MyVideos*.db` `files` table, so it works for Ororo plugin URLs without needing the show to be in Kodi's scraped library.
- **Mark show/season watched or unwatched.** Context menu entries on Favourites, Subscriptions, and season rows. Works on never-played episodes (inserts the necessary `files` rows) and on previously played ones (updates existing rows).
- **Reset watched state.** Root-level action that clears all Ororo playcounts — undo lever if anything goes wrong.

### Packaging
- Android Kodi's zip parser rejects Unix extended attributes. Build with Python's `zipfile` module (FAT-format) or use `zip -X`. See [AGENTS.md](AGENTS.md) and the Building section below.

See [CHANGELOG.md](CHANGELOG.md) for the full history.

## Requirements

- Kodi 19 (Matrix) or later
- Ororo.tv subscription

## Installation

1. Download the latest `plugin.video.ororotv-x.x.x.zip` from [Releases](../../releases)
2. In Kodi: **Add-ons** → **Install from zip file**
3. Select the downloaded zip file

### Android Kodi

The zip must be built without Unix extended attributes or the Android unpacker rejects it. See [AGENTS.md](AGENTS.md) for the packaging recipe — or use the Python-based build (below), which produces a FAT-format zip that works everywhere.

## Configuration

1. Open the addon settings
2. Enter your Ororo.tv email and password

## How watched state is tracked

Ororo episodes aren't scraped into Kodi's TV library — they play directly from plugin URLs. The addon reads and writes `playCount` on those URLs in Kodi's `MyVideos*.db` `files` table directly. Marking a season watched on a fresh show INSERTs rows into that table. If `VideoLibrary.Clean` ever runs, synthetic rows may be pruned; use **Reset watched state** and re-mark if that happens.

## Building

```bash
python3 - <<'EOF'
import zipfile, os
src = 'plugin.video.ororotv'
with zipfile.ZipFile(f'{src}.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk('.'):
        for f in files:
            if f.endswith('.pyc'): continue
            p = os.path.join(root, f)
            zi = zipfile.ZipInfo(f'{src}/' + os.path.relpath(p, '.'))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zi.create_system = 0
            zf.writestr(zi, open(p, 'rb').read())
EOF
```

Python's `zipfile` produces a clean FAT-format zip that installs on both desktop and Android Kodi.

## License

GPLv3 — see [LICENSE.txt](LICENSE.txt)

# Ororo.tv Kodi Addon

Kodi addon for streaming movies and TV shows from [Ororo.tv](https://ororo.tv).

This is a fork of the upstream addon with fixes for Kodi 19+ and additions around watched-state tracking. See [CHANGELOG.md](CHANGELOG.md) for the full history.

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

## Features beyond upstream

- **Fast Favourites/Subscriptions.** Per-show API calls now run in parallel (10 workers) and use the plugin's cache. Opening a large Favourites list went from ~20× sequential requests to ~2× parallel.
- **Unwatched-episode counter.** Shows and seasons in Favourites/Subscriptions display as `Show Name (N)` where `N` is the number of episodes you haven't played yet. Suppressed when zero.
- **Mark as watched.** Right-click a show or season in Favourites/Subscriptions to mark it watched or unwatched. Works on never-played episodes too.
- **Reset watched state.** Root-level action that clears all Ororo playcounts — useful if marking goes wrong.
- **Python 3 cache fix.** The upstream cache silently did nothing on Kodi 19+ because `hashlib.md5().update(str(x))` throws on Python 3. Fixed to encode to UTF-8 bytes first.

### How watched state is tracked

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

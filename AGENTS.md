# Packaging Kodi Plugin for Distribution

## Creating a Zip File for Kodi

When packaging this plugin for Kodi, the zip file must be created **without Unix extended attributes**. Android Kodi's zip handler cannot properly parse Unix extra fields (UT timestamps and ux UID/GID) and will fail with an "invalid structure" error.

### Correct Command

```bash
zip -r -X plugin.video.ororotv-VERSION.zip plugin.video.ororotv-VERSION/
```

The `-X` flag is critical - it excludes extra file attributes that break Android compatibility.

### Why This Matters

- Zips created on macOS/Linux without `-X` include Unix extended attributes
- These attributes add extra bytes to each file header in the zip
- Android Kodi's zip parser doesn't handle these correctly
- macOS/Windows Kodi is more lenient and works regardless

### Verifying the Zip

To check if a zip has problematic extra attributes:

```bash
zipinfo your-plugin.zip | head -5
```

- Good: `drwxr-xr-x  3.0 unx   0 b- stor ...` (no `x` after `b`)
- Bad: `drwxr-xr-x  3.0 unx   0 bx stor ...` (has `x` = extra fields)

Or check the hex header - extra field length should be `0000`:

```bash
xxd your-plugin.zip | head -3
```

Look at bytes 0x1e-0x1f - should be `0000`, not `1c00` or similar.

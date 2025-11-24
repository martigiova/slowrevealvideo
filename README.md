# Batch Instagram Reels → MP3

This repository rebuilds the original Italian project in English and focuses on a
single task: take a list of Instagram Reel links, extract their audio tracks
with `ffmpeg`, and drop the resulting MP3 files into a brand-new folder for each
run. The downloader is cross-platform and works on both macOS and Windows as
long as Python 3.10+ and `ffmpeg` are available.

## Highlights

- Batch mode that reads every link from `links.txt` (comments and blank lines are ignored)
- Uses `yt-dlp` + `ffmpeg` to grab the best available audio and transcode to MP3
- Automatically creates `downloads/batch-YYYYmmdd-HHMMSS` for every run so files never mix
- Configurable bitrate (128/192/256/320 kbps) and optional graceful error handling
- Helper launchers for macOS (`scripts/run-macos.sh`) and Windows (`scripts/run-windows.ps1`)

## Requirements

- Python 3.10 or newer
- `ffmpeg` accessible from your `PATH` (or provide a path via `--ffmpeg`)
- `pip` to install the lone dependency: `yt-dlp`

### Installing ffmpeg

- **macOS**: `brew install ffmpeg`
- **Windows**: Download a static build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), unzip, and add the `bin` folder to your `PATH`

Verify the install with:

```bash
ffmpeg -version
```

## Setup

### macOS / Linux

```bash
git clone <this-repo-url>
cd <repo>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
git clone <this-repo-url>
Set-Location <repo>
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## Provide Your Reel Links

Edit `links.txt` and paste one Reel URL per line, e.g.

```
https://www.instagram.com/reel/EXAMPLEID1/
https://www.instagram.com/reel/EXAMPLEID2/
```

Lines that start with `#` are treated as comments and skipped.

## Running the Downloader

### Generic CLI

```bash
python3 reels_batch_downloader.py --links links.txt --output-dir downloads
```

Each run creates a unique directory such as `downloads/batch-20250111-153055`
and places all MP3 files inside it. To keep going after a failure, add
`--ignore-errors`. To limit how many links are processed, add `--limit 5`.

### macOS helper

```bash
./scripts/run-macos.sh --links links.txt
```

### Windows helper

```powershell
pwsh scripts/run-windows.ps1 --links links.txt
```

Both helpers simply forward every argument to the Python script, so you can use
flags like `--quality 192` or `--ffmpeg "C:\\ffmpeg\\bin\\ffmpeg.exe"`.

## Command Options

| Flag | Description | Default |
|------|-------------|---------|
| `--links / -l` | Text file that contains Instagram URLs | `links.txt` |
| `--output-dir / -o` | Base folder where run-specific directories are created | `downloads` |
| `--quality / -q` | MP3 bitrate: 128, 192, 256, 320 | `320` |
| `--ffmpeg` | Absolute path to `ffmpeg` if it is not on PATH | auto-detect |
| `--limit` | Only download the first *N* links | Process all |
| `--ignore-errors` | Continue even if a download fails | Stop at first failure |
| `--verbose` | Print debug logs from yt-dlp | Disabled |

## Output

- `downloads/batch-*/` — new folder per run containing all MP3 files
- Filenames follow `uploadDate__id__title.mp3`
- Exit code `0` means all downloads succeeded, `2` means at least one failed

## Notes

- Instagram frequently changes its APIs; if a download suddenly fails, update
  `yt-dlp` with `pip install --upgrade yt-dlp`.
- Respect Instagram’s Terms of Service and local copyright laws. This project
  is meant for personal/offline use.*** End Patch
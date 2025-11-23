# Slow Reveal Video Batch Tool

Desktop app for Windows and macOS that applies a smooth “slow reveal” pan from bottom to top across batches of vertical clips. Load every video, pick the export folder, and let the processor animate the frame with progressive zoom + easing so your reels feel dynamic without manual keyframes.

---

## Step 1 – Download the ready-made ZIP
- Grab the bundle directly from Cursor: [SlowRevealVideo_windows.zip](./SlowRevealVideo_windows.zip)
- Requirements on the target machine: Python 3.10+ installed system-wide and `ffmpeg` available on `PATH` (MoviePy uses it under the hood).

## Step 2 – Extract the ZIP
1. Unzip `SlowRevealVideo_windows.zip` (some unzip tools create an extra wrapper folder; open the inner folder if needed).
2. Inside you’ll find:
   - `Start SlowRevealVideo.bat` (Windows launcher that provisions a local virtualenv)
   - `Start SlowRevealVideo.command` (macOS launcher; run `chmod +x` the first time)
   - `slowreveal/` package with the GUI + processor code
   - `requirements.txt`, `pyproject.toml`
   - Empty `exports/` folder where renders will be placed
   - Optional `samples/` folder where you can drop demo clips
   - `README.txt` with the same quick instructions

## Step 3 – Launch the application
1. **Windows**: double-click `Start SlowRevealVideo.bat`. The script creates `.venv`, installs dependencies, and launches the Tkinter UI. First run may take a minute while pip downloads MoviePy.
2. **macOS**: double-click `Start SlowRevealVideo.command` (after `chmod +x`). It performs the same automated setup.
3. Keep the folder open while working—the launchers expect to be run from that directory so they can find the bundled package.

## Step 4 – Load your vertical clips
1. Click **Add videos…** and select every `.mp4`, `.mov`, `.mkv`, etc. you want to process (feel free to drop 20+ files at once).
2. Use **Remove selected** or **Clear list** if you loaded the wrong clips.
3. The live log flags horizontal clips with a ⚠️ so you know which exports may need manual tweaks later.

## Step 5 – Pick the export folder and tweak parameters
- **Destination folder** defaults to the extracted directory. Click **Choose folder…** to point to a faster SSD or shared drive.
- **Zoom factor (>= 1.1)** controls how much the framing tightens over time. 1.6–2.2 works well for most Reels/TikToks.
- **Easing power** shapes the camera motion (0.8–1.0 keeps it gentle, < 0.8 speeds up the opening reveal).
- **Output suffix** appends text to each filename, e.g., `_slowreveal` or `_zoom`.

## Step 6 – Convert the batch
1. Hit **Start processing**.
2. Follow the progress bar and log entries (`✅ clip.mov → clip_slowreveal.mp4`) as each clip finishes.
3. Open the export folder to grab the ready-to-edit MP4 files for Premiere, CapCut, or DaVinci.

## Tips & Troubleshooting
- **Large batches (50+ clips)**: split into 20–25 items if you’re on a laptop or limited CPU.
- **Letterboxed clips**: bump `Zoom factor` slightly to hide black bars, or trim later in your NLE.
- **ffmpeg errors**: ensure `ffmpeg` is installed and reachable from the same terminal where the launcher runs.
- **Performance**: keep the machine plugged in and export to a fast SSD to avoid dropped frames.
- **ModuleNotFoundError for moviepy**: delete the `.venv` folder inside the bundle and relaunch the script; the launcher will recreate the env and reinstall dependencies using the correct interpreter.

---

## Developer mode

### Requirements
- Python 3.10+
- `ffmpeg` on `PATH`

### Local setup
```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m slowreveal
```

### Build distributables
Run these commands on the target OS (Windows for `.exe`, macOS for `.app`):

```bash
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --windowed --onefile \
  --name SlowRevealVideo \
  src/slowreveal/app.py
```

Artifacts appear under `dist/SlowRevealVideo*`. Zip the output together with `ffmpeg`/`ffprobe` if you want a portable drop-in bundle.

### Project structure
```
src/slowreveal/
├── __main__.py      # python -m slowreveal entry point
├── app.py           # Tkinter UI with batch controls
└── processor.py     # MoviePy-based slow reveal logic
```

Increase `Zoom factor` for a more dramatic move; use `Easing power < 1` for a faster reveal. Horizontal videos are still processed, but the log warns you so you can review them manually.
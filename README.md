# Slow Reveal GUI (Feet → Head 9:16)

Single-file Tkinter app (`slowreveal_gui.py`) that applies the “feet-to-head” slow reveal to as many vertical clips as you want. The UI matches the screenshot you shared: select the inputs, pick an output folder, tweak zoom/easing, then hit **Start batch** to export files like `video.mp4 → video_slowreveal.mp4`.

---

## Requirements

- Python 3.10 or newer (Windows or macOS).
- `ffmpeg` installed and reachable via `PATH`.
- MoviePy (install once): `pip install moviepy`  
  *(or run `pip install -r requirements.txt`, which simply lists `moviepy>=1.0.3`).*

---

## Setup & Launch

### Windows (PowerShell)
```powershell
git clone https://github.com/…/slowrevealvideo.git
cd slowrevealvideo
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install moviepy
py -3 slowreveal_gui.py
```

### macOS / Linux (Terminal)
```bash
git clone https://github.com/.../slowrevealvideo.git
cd slowrevealvideo
python3 -m venv .venv
source .venv/bin/activate
pip install moviepy
python3 slowreveal_gui.py
```

> Tip: if you only need the script, download `slowreveal_gui.py`, `requirements.txt`, and run the same `pip install moviepy` + `python slowreveal_gui.py` commands from that folder.

---

## Using the GUI

1. **Select videos** – pick as many `.mp4`, `.mov`, `.m4v` vertical clips as you need (50 at once is fine).
2. **Select folder** – choose where the processed files will be written.
3. *(Optional)* Adjust **Zoom factor** (>1.5 for tighter crops) and **Easing power** (<1 accelerates the start of the move).
4. Click **Start batch** – the log panel shows progress (`✅ file_slowreveal.mp4`) and any warnings (e.g., non-vertical sources).

Exports keep the original extension and append `_slowreveal`, e.g. `original.mp4 → original_slowreveal.mp4`.

---

## Troubleshooting & Tips

- **No UI / Tkinter errors** – ensure you are running the system Python that ships with Tk (on macOS, use `/usr/bin/python3` or the official installer, not Conda without Tk support).
- **`ffmpeg` missing** – install it via Homebrew (`brew install ffmpeg`) or download the Windows build and add it to `PATH`.
- **Batch performance** – long batches go faster on SSDs; keep laptops plugged in to avoid throttling.
- **Letterboxed footage** – raise the zoom factor slightly to crop out black bars.
- **Resetting the env** – delete `.venv` (if you created one) and reinstall `moviepy` if pip dependencies get out of sync.

That’s it—run `python slowreveal_gui.py`, follow the four UI steps, and you’ll get the same interface illustrated in your attachment with ready-to-edit `_slowreveal` clips.
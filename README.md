# ConvertiIG2MP3 – Bulk Instagram Audio Downloader

Easily download dozens of Instagram Reel audios at once and automatically convert them to MP3 files for your editing workflow. The packaged Windows build bundles everything you need, including `ffmpeg`, so no extra setup is required.

## Step 1 – Download the Build
1. Open the latest successful GitHub Actions run: https://github.com/webelieveinai25/ig2mp3-repo/actions/runs/17186057031
2. Sign in to GitHub if prompted (Actions artifacts require an authenticated session).
3. Scroll to the *Artifacts* section and download `ConvertiIG2MP3_windows.zip`.

## Step 2 – Extract the ZIP
1. Locate the downloaded `ConvertiIG2MP3_windows.zip`.
2. Right-click → *Extract All…*. Some browsers wrap the payload in an extra folder—if you see another ZIP inside, extract it as well so you end up with the actual app directory.
3. After extraction you should see:
   - `ConvertiIG2MP3.exe`
   - `ffmpeg.exe`
   - `README.txt`
   - `links.txt` (example input list)
   - `output_mp3/` (default export folder)

## Step 3 – Launch the App
1. Double-click `ConvertiIG2MP3.exe`.
2. If Windows SmartScreen warns you, choose **More info → Run anyway** (the build is unsigned, so this is expected).
3. Wait for the GUI window to open—keep the folder open while the program runs.

## Step 4 – Paste Instagram Links
1. In Instagram, copy the Reel URLs you want to process.
2. Paste one or many (up to ~50 at a time) into the large text box in the app.
3. Optional: click **Load from file** and select `links.txt` (or any `.txt` you curate) to prefill the list.

## Step 5 – Choose the Output Folder
- By default, finished MP3 files land in the bundled `output_mp3` folder.
- Click **Choose folder** if you want to save them elsewhere (e.g., a synced drive).

## Step 6 – Convert to MP3
1. Hit **Convert to MP3**.
2. The status log will show each download and conversion. Keep the window open until every link reports *Done*.
3. Open the chosen folder to confirm the MP3 files; they’re named after the Reel IDs for easy tracking.

## Tips & Troubleshooting
- **Failed download?** Re-copy the Instagram URL from the Share sheet to ensure it’s the full permalink, then retry.
- **Large batches:** Run in smaller chunks (e.g., 20–25 links) if your network is unstable.
- **Antivirus flags:** Add the folder to your AV allow-list; unsigned executables can trigger generic warnings even when safe.
- **Keep ffmpeg nearby:** Don’t move `ffmpeg.exe` out of the folder; the app calls it directly for audio conversion.

With these steps in your GitHub README or documentation, teammates can reproduce the entire download → convert workflow without guesswork.
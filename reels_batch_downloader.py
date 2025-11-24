#!/usr/bin/env python3
"""
Batch download Instagram Reels audio tracks using yt-dlp + ffmpeg.

The script reads a text file containing Instagram URLs, downloads each reel,
and saves the extracted MP3 files into a freshly created run directory.
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import shutil
import sys
from pathlib import Path
from typing import List, Sequence

import yt_dlp

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the audio tracks from a batch of Instagram Reels.",
    )
    parser.add_argument(
        "--links",
        "-l",
        default="links.txt",
        help="Path to the text file that contains Instagram URLs (default: links.txt).",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="downloads",
        help="Base directory where a unique folder will be created for this run.",
    )
    parser.add_argument(
        "--quality",
        "-q",
        default="320",
        choices=["128", "192", "256", "320"],
        help="MP3 bitrate in kbps (default: 320).",
    )
    parser.add_argument(
        "--ffmpeg",
        help="Optional path to the ffmpeg binary. Set only if ffmpeg is not on PATH.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only process the first N links from the list.",
    )
    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Continue processing other links even if one download fails.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logs for troubleshooting.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)


def load_links(path: Path, limit: int | None = None) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Links file not found: {path}")

    lines: List[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("#"):
                continue
            lines.append(cleaned)
            if limit and len(lines) >= limit:
                break

    if not lines:
        raise ValueError(f"No download links found inside {path}")

    return lines


def ensure_ffmpeg(ffmpeg_arg: str | None) -> str:
    if ffmpeg_arg:
        binary = Path(ffmpeg_arg).expanduser().resolve()
        if not binary.is_file():
            raise FileNotFoundError(f"ffmpeg binary not found at {binary}")
        return str(binary)

    detected = shutil.which("ffmpeg")
    if detected:
        return detected

    raise RuntimeError(
        "ffmpeg was not found on PATH. Install ffmpeg and/or pass --ffmpeg /path/to/ffmpeg.",
    )


def create_run_directory(base_dir: Path) -> Path:
    """
    Create a time-based folder and make sure it is unique even when invoked
    multiple times within the same second.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = base_dir / f"batch-{timestamp}"
    counter = 1
    while candidate.exists():
        candidate = base_dir / f"batch-{timestamp}-{counter}"
        counter += 1
    candidate.mkdir()
    return candidate


def download_audio(
    urls: Sequence[str],
    destination: Path,
    quality: str,
    ffmpeg_binary: str,
    ignore_errors: bool,
) -> tuple[list[Path], list[tuple[str, str]]]:
    successes: list[Path] = []
    failures: list[tuple[str, str]] = []

    outtmpl = str(destination / "%(upload_date)s__%(id)s__%(title).80s.%(ext)s")

    ydl_common_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
        "ffmpeg_location": ffmpeg_binary,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
    }

    for idx, url in enumerate(urls, start=1):
        logging.info("(%d/%d) Downloading %s", idx, len(urls), url)
        try:
            with yt_dlp.YoutubeDL(ydl_common_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
            if filename.exists():
                successes.append(filename)
                logging.info("Saved %s", filename.name)
            else:
                msg = "Download finished but mp3 file was not found"
                failures.append((url, msg))
                logging.error("%s: %s", msg, url)
                if not ignore_errors:
                    break
        except Exception as exc:  # noqa: BLE001
            failures.append((url, str(exc)))
            logging.error("Failed to process %s: %s", url, exc)
            if not ignore_errors:
                break

    return successes, failures


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    links_file = Path(args.links)
    base_output_dir = Path(args.output_dir)

    try:
        urls = load_links(links_file, args.limit)
        ffmpeg_bin = ensure_ffmpeg(args.ffmpeg)
        run_dir = create_run_directory(base_output_dir)
    except Exception as exc:  # noqa: BLE001
        logging.error("%s", exc)
        return 1

    logging.info("Processing %d links", len(urls))
    logging.info("Output folder: %s", run_dir)

    successes, failures = download_audio(
        urls=urls,
        destination=run_dir,
        quality=args.quality,
        ffmpeg_binary=ffmpeg_bin,
        ignore_errors=args.ignore_errors,
    )

    logging.info("Completed downloads: %d", len(successes))
    if failures:
        logging.warning("Failed downloads: %d", len(failures))
        for url, error in failures:
            logging.warning("%s -> %s", url, error)

    logging.info(
        "All MP3 files for this run are stored in: %s",
        run_dir,
    )

    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())

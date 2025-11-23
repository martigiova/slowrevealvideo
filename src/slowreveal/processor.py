from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from moviepy.editor import VideoFileClip


@dataclass
class SlowRevealSettings:
    """Configuration values that shape the virtual camera movement."""

    zoom_factor: float = 1.8
    easing_power: float = 0.9
    preset: str = "medium"
    codec: str = "libx264"
    audio_codec: str = "aac"
    output_suffix: str = "_slowreveal"

    def validate(self) -> None:
        if self.zoom_factor <= 1.0:
            raise ValueError("zoom_factor deve essere maggiore di 1.0 per abilitare lo zoom.")
        if self.easing_power <= 0:
            raise ValueError("easing_power deve essere positivo.")
        if not self.output_suffix:
            self.output_suffix = "_slowreveal"


@dataclass
class ProcessingReport:
    """Information about a processed clip."""

    output_path: Path
    source_resolution: Tuple[int, int]
    warned_orientation: bool


class SlowRevealProcessor:
    """Run the slow-reveal effect on one or more video files."""

    def process_file(
        self,
        input_path: Path,
        output_dir: Path,
        settings: Optional[SlowRevealSettings] = None,
    ) -> ProcessingReport:
        settings = settings or SlowRevealSettings()
        settings.validate()

        input_path = input_path.expanduser().resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"File non trovato: {input_path}")

        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}{settings.output_suffix}{input_path.suffix}"

        warned_orientation, resolution = self._apply_slow_reveal(input_path, output_path, settings)

        return ProcessingReport(
            output_path=output_path,
            source_resolution=resolution,
            warned_orientation=warned_orientation,
        )

    @staticmethod
    def _apply_slow_reveal(
        input_path: Path,
        output_path: Path,
        settings: SlowRevealSettings,
    ) -> Tuple[bool, Tuple[int, int]]:
        warned_orientation = False

        with VideoFileClip(str(input_path)) as clip:
            width, height = clip.size
            fps = clip.fps or 30

            if height <= width:
                warned_orientation = True

            crop_w = max(1, int(width / settings.zoom_factor))
            crop_h = max(1, int(height / settings.zoom_factor))
            x1_fixed = (width - crop_w) // 2
            x2_fixed = x1_fixed + crop_w
            y_start = height - crop_h
            y_end = 0
            duration = max(clip.duration, 0.01)

            def dynamic_crop(get_frame, t):
                frame = get_frame(t)
                progress = min(1.0, max(0.0, t / duration))
                eased = progress ** settings.easing_power
                y1 = int(y_start * (1 - eased) + y_end * eased)
                y1 = max(0, min(y1, height - crop_h))
                y2 = y1 + crop_h
                return frame[y1:y2, x1_fixed:x2_fixed]

            cropped_clip = clip.fl(dynamic_crop, apply_to=["mask"])
            final_clip = cropped_clip.resize((width, height))

            try:
                final_clip.write_videofile(
                    str(output_path),
                    codec=settings.codec,
                    audio_codec=settings.audio_codec,
                    preset=settings.preset,
                    fps=fps,
                    verbose=False,
                    logger=None,
                )
            finally:
                if hasattr(final_clip, "close"):
                    final_clip.close()
                if hasattr(cropped_clip, "close"):
                    cropped_clip.close()

        return warned_orientation, (width, height)

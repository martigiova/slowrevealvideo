from __future__ import annotations

import importlib
import subprocess
import sys
from typing import List


def _ensure_runtime_dependencies() -> None:
    """
    Lazily install heavy runtime packages (moviepy, imageio-ffmpeg) into the
    interpreter currently running the GUI. This is mainly a safety net for
    users launching the portable bundle without having pip-installed the
    requirements beforehand.
    """

    required_specs = ["moviepy>=1.0.3", "imageio-ffmpeg>=0.4.9"]
    missing: List[str] = []

    try:
        import moviepy.editor  # noqa: F401  # pragma: no cover - runtime only
    except ModuleNotFoundError:
        missing.append(required_specs[0])

    try:
        import imageio_ffmpeg  # noqa: F401  # pragma: no cover - runtime only
    except ModuleNotFoundError:
        missing.append(required_specs[1])

    if missing:
        print("[SlowReveal] Installing missing dependencies:", ", ".join(missing))
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover
            raise SystemExit(
                "Unable to install runtime dependencies automatically. "
                "Please ensure pip is available and rerun the launcher."
            ) from exc

        importlib.invalidate_caches()
        for name in ("moviepy", "moviepy.editor", "imageio_ffmpeg"):
            sys.modules.pop(name, None)

    # Final validation so we fail early with a clear message.
    for module_name in ("moviepy.editor", "imageio_ffmpeg"):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise SystemExit(
                f"Required dependency '{module_name}' is still missing after installation. "
                "Run pip manually inside the virtual environment and retry."
            ) from exc


_ensure_runtime_dependencies()

from slowreveal.app import run


if __name__ == "__main__":
    run()

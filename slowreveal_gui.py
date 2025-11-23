import os
import tkinter as tk
from tkinter import filedialog, messagebox

from moviepy.editor import VideoFileClip

# Default UI values (safe for most 9:16 reels)
DEFAULT_ZOOM_FACTOR = 1.8   # >1.5 tightens the crop aggressively
DEFAULT_EASING_POWER = 0.9  # <1 speeds up the beginning of the move
VALID_EXT = (".mp4", ".mov", ".m4v")


def process_video(input_path, output_dir, zoom_factor, easing_power, log_callback=None):
    """Apply the feet→head slow reveal to a single video."""
    if log_callback:
        log_callback(f"▶️ Processing: {os.path.basename(input_path)}")

    clip = None
    final_clip = None
    try:
        clip = VideoFileClip(input_path)
        width, height = clip.size

        if height <= width and log_callback:
            log_callback(f"  ⚠️ Non-vertical (W={width}, H={height}) – expect letterboxing")

        crop_w = int(width / zoom_factor)
        crop_h = int(height / zoom_factor)
        x1_fixed = (width - crop_w) // 2
        x2_fixed = x1_fixed + crop_w
        y_start = height - crop_h  # start anchored to the feet
        y_end = 0                  # finish at the head

        def dynamic_crop(get_frame, t):
            frame = get_frame(t)
            duration = max(clip.duration, 0.01)
            progress = min(1.0, max(0.0, t / duration))
            eased = progress ** easing_power
            y1 = int(y_start * (1 - eased) + y_end * eased)
            y1 = max(0, min(y1, height - crop_h))
            y2 = y1 + crop_h
            return frame[y1:y2, x1_fixed:x2_fixed]

        cropped_clip = clip.fl(dynamic_crop, apply_to=["mask"])
        final_clip = cropped_clip.resize((width, height))

        base = os.path.basename(input_path)
        name, ext = os.path.splitext(base)
        out_path = os.path.join(output_dir, f"{name}_slowreveal{ext}")

        if log_callback:
            log_callback("  💾 Exporting...")

        final_clip.write_videofile(
            out_path,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            fps=clip.fps,
        )

        if log_callback:
            log_callback(f"  ✅ Done → {os.path.basename(out_path)}")

    except Exception as exc:
        message = f"  ❌ Error: {exc}"
        if log_callback:
            log_callback(message)
        else:
            print(message)
    finally:
        if final_clip is not None:
            final_clip.close()
        if clip is not None:
            clip.close()


class SlowRevealApp:
    """Minimal Tkinter GUI for batching slow-reveal exports."""

    def __init__(self, root):
        self.root = root
        self.root.title("Slow Reveal Batch Tool (Feet → Head 9:16)")
        self.root.geometry("720x520")

        self.selected_files = []
        self.output_dir = ""

        self._build_inputs()
        self._build_outputs()
        self._build_settings()
        self._build_start_button()
        self._build_log_area()

    # ------------------------------------------------------------------ UI builders
    def _build_inputs(self):
        frame = tk.LabelFrame(self.root, text="Input videos", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        self.files_label = tk.Label(frame, text="No files selected")
        self.files_label.pack(side="left", expand=True, fill="x")

        tk.Button(frame, text="Select videos", command=self.select_files).pack(side="right")

    def _build_outputs(self):
        frame = tk.LabelFrame(self.root, text="Output folder", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        self.output_label = tk.Label(frame, text="No folder selected")
        self.output_label.pack(side="left", expand=True, fill="x")

        tk.Button(frame, text="Select folder", command=self.select_output_folder).pack(side="right")

    def _build_settings(self):
        frame = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Zoom factor:").grid(row=0, column=0, sticky="w")
        self.zoom_var = tk.StringVar(value=str(DEFAULT_ZOOM_FACTOR))
        tk.Entry(frame, textvariable=self.zoom_var, width=8).grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(frame, text="Easing power:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.easing_var = tk.StringVar(value=str(DEFAULT_EASING_POWER))
        tk.Entry(frame, textvariable=self.easing_var, width=8).grid(row=0, column=3, sticky="w", padx=5)

    def _build_start_button(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill="x")

        self.start_button = tk.Button(frame, text="Start batch", command=self.start_batch, height=2)
        self.start_button.pack(fill="x")

    def _build_log_area(self):
        frame = tk.LabelFrame(self.root, text="Log", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(frame, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    # ------------------------------------------------------------------ Helpers
    def log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        print(message)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select vertical videos (9:16)",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.m4v"),
                ("All files", "*.*"),
            ],
        )
        if files:
            self.selected_files = list(files)
            self.files_label.config(text=f"{len(self.selected_files)} file(s) selected")
            self.log(f"Selected {len(self.selected_files)} file(s).")
        else:
            self.selected_files = []
            self.files_label.config(text="No files selected")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=self.output_dir)
            self.log(f"Output folder set to: {self.output_dir}")
        else:
            self.output_dir = ""
            self.output_label.config(text="No folder selected")

    def start_batch(self):
        if not self.selected_files:
            messagebox.showwarning("No videos", "Please select at least one input video.")
            return
        if not self.output_dir:
            messagebox.showwarning("No output folder", "Please select an output folder.")
            return

        try:
            zoom_factor = float(self.zoom_var.get())
            easing_power = float(self.easing_var.get())
        except ValueError:
            messagebox.showerror("Invalid parameters", "Zoom factor and easing power must be numbers.")
            return

        self.start_button.config(state="disabled")
        self.log("===== Starting batch processing =====")
        self.log(f"Zoom factor: {zoom_factor}, Easing power: {easing_power}")
        self.root.update_idletasks()

        for index, path in enumerate(self.selected_files, start=1):
            name = os.path.basename(path)
            if not path.lower().endswith(VALID_EXT):
                self.log(f"⏭ Skipping (unsupported extension): {name}")
                continue

            self.log(f"\n[{index}/{len(self.selected_files)}] {name}")
            process_video(path, self.output_dir, zoom_factor, easing_power, log_callback=self.log)

        self.log("\n🎉 Batch finished!")
        self.start_button.config(state="normal")
        messagebox.showinfo("Done", "Batch processing completed.")


def main():
    root = tk.Tk()
    app = SlowRevealApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

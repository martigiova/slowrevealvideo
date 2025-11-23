from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List

from slowreveal.processor import ProcessingReport, SlowRevealProcessor, SlowRevealSettings

VIDEO_FILE_TYPES = [
    ("Video files", "*.mp4 *.mov *.m4v *.mkv *.avi"),
    ("MP4", "*.mp4"),
    ("MOV", "*.mov"),
    ("All files", "*.*"),
]


class SlowRevealApp(tk.Tk):
    """Simple Tkinter GUI that wraps SlowRevealProcessor for batch jobs."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Slow Reveal Batch Processor")
        self.geometry("880x600")
        self.minsize(720, 520)

        self.processor = SlowRevealProcessor()
        self.selected_files: List[str] = []
        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        self.zoom_var = tk.StringVar(value="1.8")
        self.easing_var = tk.StringVar(value="0.9")
        self.suffix_var = tk.StringVar(value="_slowreveal")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Seleziona uno o più video per iniziare.")

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker_thread: threading.Thread | None = None
        self.control_widgets: List[tk.Widget] = []

        self._build_ui()
        self.after(150, self._poll_log_queue)

    # ------------------------------------------------------------------ UI setup
    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        # File selection
        files_frame = ttk.LabelFrame(main, text="Video da elaborare", padding=8)
        files_frame.pack(fill="both", expand=True)

        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill="both", expand=True)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        buttons_frame = ttk.Frame(files_frame)
        buttons_frame.pack(fill="x", pady=(8, 0))

        self._add_button(buttons_frame, "Aggiungi video…", self._add_files)
        self._add_button(buttons_frame, "Rimuovi selezionati", self._remove_selected)
        self._add_button(buttons_frame, "Svuota lista", self._clear_files)

        # Configuration
        config_frame = ttk.LabelFrame(main, text="Impostazioni effetto", padding=8)
        config_frame.pack(fill="x", pady=12)

        ttk.Label(config_frame, text="Zoom factor (>=1.1)").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(config_frame, textvariable=self.zoom_var, width=10).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        ttk.Label(config_frame, text="Easing power").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(config_frame, textvariable=self.easing_var, width=10).grid(row=1, column=1, sticky="w", padx=4, pady=2)

        ttk.Label(config_frame, text="Suffisso output").grid(row=0, column=2, sticky="w", padx=4, pady=2)
        ttk.Entry(config_frame, textvariable=self.suffix_var, width=20).grid(row=0, column=3, sticky="w", padx=4, pady=2)

        for i in range(4):
            config_frame.columnconfigure(i, weight=1 if i % 2 == 1 else 0)

        # Output directory
        output_frame = ttk.LabelFrame(main, text="Cartella di destinazione", padding=8)
        output_frame.pack(fill="x")

        ttk.Entry(output_frame, textvariable=self.output_dir, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._add_button(output_frame, "Scegli cartella…", self._choose_output_dir)

        # Progress + controls
        progress_frame = ttk.Frame(main)
        progress_frame.pack(fill="x", pady=8)

        self.progress_bar = ttk.Progressbar(progress_frame, maximum=100, variable=self.progress_var)
        self.progress_bar.pack(fill="x", expand=True)

        self.process_button = ttk.Button(main, text="Avvia elaborazione", command=self._start_processing)
        self.process_button.pack(fill="x")
        self.control_widgets.append(self.process_button)

        ttk.Label(main, textvariable=self.status_var).pack(fill="x", pady=(6, 0))

        # Log output
        log_frame = ttk.LabelFrame(main, text="Log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.log_text = tk.Text(log_frame, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def _add_button(self, parent: ttk.Widget, label: str, command) -> None:
        btn = ttk.Button(parent, text=label, command=command)
        btn.pack(side="left", padx=4)
        self.control_widgets.append(btn)

    # ------------------------------------------------------------------ File management
    def _add_files(self) -> None:
        paths = filedialog.askopenfilenames(filetypes=VIDEO_FILE_TYPES)
        if not paths:
            return
        added = 0
        for path in paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.file_listbox.insert(tk.END, path)
                added += 1
        if added:
            self._status(f"{added} video aggiunti.")

    def _remove_selected(self) -> None:
        selection = list(self.file_listbox.curselection())
        if not selection:
            return
        for index in reversed(selection):
            self.file_listbox.delete(index)
            del self.selected_files[index]
        self._status("Video selezionati rimossi.")

    def _clear_files(self) -> None:
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self._status("Lista svuotata.")

    # ------------------------------------------------------------------ Output dir
    def _choose_output_dir(self) -> None:
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
            self._status(f"Cartella di output: {directory}")

    # ------------------------------------------------------------------ Processing
    def _start_processing(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Elaborazione in corso", "Attendi che il batch corrente finisca.")
            return

        if not self.selected_files:
            messagebox.showwarning("Nessun file", "Aggiungi almeno un video.")
            return

        try:
            zoom = float(self.zoom_var.get())
            easing = float(self.easing_var.get())
        except ValueError:
            messagebox.showerror("Valori non validi", "Inserisci numeri per zoom ed easing.")
            return

        suffix = self.suffix_var.get().strip() or "_slowreveal"
        settings = SlowRevealSettings(zoom_factor=zoom, easing_power=easing, output_suffix=suffix)

        output_dir = Path(self.output_dir.get())
        self._toggle_controls(disabled=True)
        self.progress_var.set(0.0)
        self._status("Elaborazione in corso…")
        self._log(f"Inizio batch su {len(self.selected_files)} file.")

        self.worker_thread = threading.Thread(
            target=self._process_files,
            args=(settings, output_dir, list(self.selected_files)),
            daemon=True,
        )
        self.worker_thread.start()

    def _process_files(self, settings: SlowRevealSettings, output_dir: Path, files: List[str]) -> None:
        total = len(files)
        for index, filepath in enumerate(files, start=1):
            path = Path(filepath)
            try:
                report = self.processor.process_file(path, output_dir, settings)
                self._handle_success(report, path)
            except Exception as exc:  # noqa: BLE001 - want to show any issue
                self._log(f"❌ Errore su {path.name}: {exc}")
            finally:
                progress = (index / total) * 100
                self._async(self.progress_var.set, progress)

        self._log("Batch completato.")
        self._async(self._on_processing_complete)

    def _handle_success(self, report: ProcessingReport, source_path: Path) -> None:
        warning = " (attenzione: video orizzontale)" if report.warned_orientation else ""
        self._log(f"✅ {source_path.name} → {report.output_path.name}{warning}")

    def _on_processing_complete(self) -> None:
        self._toggle_controls(disabled=False)
        self._status("Elaborazione completata.")

    # ------------------------------------------------------------------ Helpers
    def _toggle_controls(self, disabled: bool) -> None:
        state = "disabled" if disabled else "normal"
        for widget in self.control_widgets:
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass  # Some widgets might have been destroyed

    def _status(self, message: str) -> None:
        self.status_var.set(message)

    def _log(self, message: str) -> None:
        self.log_queue.put(message)

    def _poll_log_queue(self) -> None:
        try:
            while True:
                message = self.log_queue.get_nowait()
                self._append_log(message)
        except queue.Empty:
            pass
        finally:
            self.after(200, self._poll_log_queue)

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _async(self, func, *args) -> None:
        self.after(0, lambda: func(*args))


def run() -> None:
    app = SlowRevealApp()
    app.mainloop()


if __name__ == "__main__":
    run()

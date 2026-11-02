"""CustomTkinter GUI for Photo Converter."""

from __future__ import annotations

import logging
import platform
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from photo_converter import __version__
from photo_converter.converter import collect_images, convert_many, heif_available
from photo_converter.file_browser import ask_directory, ask_open_images
from photo_converter.formats import OUTPUT_FORMAT_LABELS
from photo_converter.i18n import LANG_DISPLAY, LANG_EN, LANG_RU, I18n

logger = logging.getLogger(__name__)


def _default_pictures_dir() -> Path:
    home = Path.home()
    for name in ("Pictures", "Images", "photos", "Photos", "Изображения"):
        candidate = home / name
        if candidate.is_dir():
            return candidate
    return home


def _resource_path(relative: str) -> Path:
    """Resolve asset path for both source and PyInstaller frozen runs."""
    import sys

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return base / relative


class PhotoConverterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.i18n = I18n()
        self.geometry("840x660")
        self.minsize(740, 580)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._selected_files: list[Path] = []
        self._output_dir: Path | None = None
        self._worker: threading.Thread | None = None
        self._cancel = threading.Event()
        self._busy = False

        self._set_icon()
        self._build_ui()
        self._apply_language()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key: str, **kwargs) -> str:
        return self.i18n.t(key, **kwargs)

    def _set_icon(self) -> None:
        icon_png = _resource_path("assets/icon.png")
        icon_ico = _resource_path("assets/icon.ico")
        try:
            if platform.system() == "Windows" and icon_ico.exists():
                self.iconbitmap(str(icon_ico))
            elif icon_png.exists():
                photo = tk.PhotoImage(file=str(icon_png))
                self.iconphoto(True, photo)
                self._icon_ref = photo
        except Exception:  # noqa: BLE001
            logger.debug("Could not set window icon", exc_info=True)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
        header.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            title_row,
            text="",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        lang_box = ctk.CTkFrame(title_row, fg_color="transparent")
        lang_box.grid(row=0, column=1, sticky="e")
        self.lang_label = ctk.CTkLabel(lang_box, text="")
        self.lang_label.grid(row=0, column=0, padx=(0, 8))
        self.lang_var = ctk.StringVar(value=LANG_DISPLAY[self.i18n.lang])
        self.lang_menu = ctk.CTkOptionMenu(
            lang_box,
            values=[LANG_DISPLAY[LANG_EN], LANG_DISPLAY[LANG_RU]],
            variable=self.lang_var,
            width=120,
            command=self._on_language_changed,
        )
        self.lang_menu.grid(row=0, column=1)

        self.heif_badge = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70"),
        )
        self.heif_badge.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.subtitle_label = ctk.CTkLabel(
            header,
            text="",
            justify="left",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray75"),
        )
        self.subtitle_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

        # --- Source selection ---
        source_frame = ctk.CTkFrame(self)
        source_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=8)
        source_frame.grid_columnconfigure(1, weight=1)

        self.source_title = ctk.CTkLabel(source_frame, text="", font=ctk.CTkFont(weight="bold"))
        self.source_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(12, 6))

        self.source_label = ctk.CTkLabel(
            source_frame,
            text="",
            anchor="w",
            text_color=("gray35", "gray70"),
        )
        self.source_label.grid(row=1, column=0, columnspan=3, sticky="ew", padx=14, pady=(0, 8))

        self.btn_select_photos = ctk.CTkButton(
            source_frame, text="", width=150, command=self._pick_files
        )
        self.btn_select_photos.grid(row=2, column=0, padx=(14, 6), pady=(0, 14))

        self.btn_select_folder = ctk.CTkButton(
            source_frame, text="", width=150, command=self._pick_folder
        )
        self.btn_select_folder.grid(row=2, column=1, padx=6, pady=(0, 14), sticky="w")

        self.btn_clear = ctk.CTkButton(
            source_frame,
            text="",
            width=100,
            fg_color=("gray70", "gray35"),
            hover_color=("gray55", "gray45"),
            command=self._clear_sources,
        )
        self.btn_clear.grid(row=2, column=2, padx=(6, 14), pady=(0, 14), sticky="e")

        # --- Options ---
        options = ctk.CTkFrame(self)
        options.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        options.grid_columnconfigure(1, weight=1)

        self.output_title = ctk.CTkLabel(options, text="", font=ctk.CTkFont(weight="bold"))
        self.output_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(12, 8))

        self.label_format = ctk.CTkLabel(options, text="")
        self.label_format.grid(row=1, column=0, sticky="w", padx=(14, 8), pady=4)
        self.format_var = ctk.StringVar(value="JPEG")
        self.format_menu = ctk.CTkOptionMenu(
            options,
            values=list(OUTPUT_FORMAT_LABELS),
            variable=self.format_var,
            width=160,
            command=self._on_format_changed,
        )
        self.format_menu.grid(row=1, column=1, sticky="w", pady=4)

        self.label_quality = ctk.CTkLabel(options, text="")
        self.label_quality.grid(row=2, column=0, sticky="w", padx=(14, 8), pady=4)
        quality_row = ctk.CTkFrame(options, fg_color="transparent")
        quality_row.grid(row=2, column=1, sticky="ew", pady=4)
        quality_row.grid_columnconfigure(0, weight=1)

        self.quality_var = ctk.IntVar(value=95)
        self.quality_slider = ctk.CTkSlider(
            quality_row,
            from_=50,
            to=100,
            number_of_steps=50,
            variable=self.quality_var,
            command=self._on_quality_changed,
        )
        self.quality_slider.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.quality_value_label = ctk.CTkLabel(quality_row, text="95", width=36)
        self.quality_value_label.grid(row=0, column=1)

        self.quality_hint = ctk.CTkLabel(
            options,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray65"),
        )
        self.quality_hint.grid(row=3, column=0, columnspan=3, sticky="ew", padx=14, pady=(2, 4))

        self.overwrite_var = ctk.BooleanVar(value=False)
        self.overwrite_cb = ctk.CTkCheckBox(options, text="", variable=self.overwrite_var)
        self.overwrite_cb.grid(row=4, column=0, columnspan=3, sticky="w", padx=14, pady=(4, 6))

        self.label_save_to = ctk.CTkLabel(options, text="")
        self.label_save_to.grid(row=5, column=0, sticky="w", padx=(14, 8), pady=4)
        self.output_label = ctk.CTkLabel(
            options,
            text="",
            anchor="w",
            text_color=("gray35", "gray70"),
        )
        self.output_label.grid(row=5, column=1, sticky="ew", pady=4)
        self.btn_choose_folder = ctk.CTkButton(
            options, text="", width=150, command=self._pick_output
        )
        self.btn_choose_folder.grid(row=5, column=2, padx=(6, 14), pady=(4, 14))

        # --- File list + log ---
        body = ctk.CTkFrame(self)
        body.grid(row=3, column=0, sticky="nsew", padx=20, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(1, weight=1)

        self.selected_files_title = ctk.CTkLabel(body, text="", font=ctk.CTkFont(weight="bold"))
        self.selected_files_title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        self.log_title = ctk.CTkLabel(body, text="", font=ctk.CTkFont(weight="bold"))
        self.log_title.grid(row=0, column=1, sticky="w", padx=12, pady=(10, 4))

        self.file_list = ctk.CTkTextbox(body, activate_scrollbars=True)
        self.file_list.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        self.file_list.configure(state="disabled")

        self.log_box = ctk.CTkTextbox(body, activate_scrollbars=True)
        self.log_box.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
        self.log_box.configure(state="disabled")

        # --- Progress + actions ---
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(4, 18))
        footer.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(footer)
        self.progress.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(footer, text="", anchor="w")
        self.status_label.grid(row=1, column=0, sticky="w")

        self.cancel_btn = ctk.CTkButton(
            footer,
            text="",
            width=120,
            state="disabled",
            fg_color=("gray70", "gray35"),
            hover_color=("gray55", "gray45"),
            command=self._cancel_conversion,
        )
        self.cancel_btn.grid(row=1, column=1, padx=(8, 8))

        self.convert_btn = ctk.CTkButton(
            footer,
            text="",
            width=160,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_conversion,
        )
        self.convert_btn.grid(row=1, column=2)

    def _on_language_changed(self, display: str) -> None:
        code = LANG_EN if display == LANG_DISPLAY[LANG_EN] else LANG_RU
        if code == self.i18n.lang:
            return
        self.i18n.set_lang(code)
        self._apply_language()
        self._log(self._t("log_lang", lang=self.i18n.display_name))

    def _apply_language(self) -> None:
        t = self._t
        self.title(t("app_title", version=__version__))
        self.title_label.configure(text=t("app_name"))
        self.lang_label.configure(text=t("language"))
        self.lang_var.set(LANG_DISPLAY[self.i18n.lang])
        self.subtitle_label.configure(text=t("subtitle"))

        if heif_available():
            self.heif_badge.configure(text=t("heif_on"))
        else:
            self.heif_badge.configure(text=t("heif_off"))

        self.source_title.configure(text=t("source_title"))
        self.btn_select_photos.configure(text=t("btn_select_photos"))
        self.btn_select_folder.configure(text=t("btn_select_folder"))
        self.btn_clear.configure(text=t("btn_clear"))

        self.output_title.configure(text=t("output_title"))
        self.label_format.configure(text=t("label_format"))
        self.label_quality.configure(text=t("label_quality"))
        self.overwrite_cb.configure(text=t("overwrite"))
        self.label_save_to.configure(text=t("label_save_to"))
        self.btn_choose_folder.configure(text=t("btn_choose_folder"))
        if self._output_dir is None:
            self.output_label.configure(text=t("not_selected"))

        self.selected_files_title.configure(text=t("selected_files"))
        self.log_title.configure(text=t("log"))
        self.cancel_btn.configure(text=t("btn_cancel"))
        self.convert_btn.configure(text=t("btn_convert"))

        if not self._busy:
            self.status_label.configure(text=t("ready"))

        self.quality_hint.configure(text=self.i18n.hint(self.format_var.get()))
        self._update_source_label()

    def _on_format_changed(self, value: str) -> None:
        self.quality_hint.configure(text=self.i18n.hint(value))
        lossy = value in ("JPEG", "WEBP", "AVIF")
        self.quality_slider.configure(state="normal" if lossy else "disabled")

    def _on_quality_changed(self, value: float) -> None:
        self.quality_value_label.configure(text=str(int(round(value))))

    def _log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_file_list(self, paths: list[Path]) -> None:
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        if not paths:
            self.file_list.insert("end", self._t("empty_list"))
        else:
            for path in paths:
                self.file_list.insert("end", f"{path.name}\n  {path.parent}\n")
        self.file_list.configure(state="disabled")

    def _update_source_label(self) -> None:
        count = len(self._selected_files)
        if count == 0:
            self.source_label.configure(text=self._t("no_files"))
        else:
            self.source_label.configure(text=self._t("files_selected", count=count))
        self._set_file_list(self._selected_files)

    def _pick_files(self) -> None:
        paths = ask_open_images(
            self,
            title=self._t("dialog_select_photos"),
            initial_dir=_default_pictures_dir(),
            t=self._t,
        )
        if not paths:
            return
        collected = collect_images(paths)
        merged = {p.resolve() for p in self._selected_files}
        merged.update(collected)
        self._selected_files = sorted(merged)
        self._update_source_label()
        self._log(self._t("log_added_picker", count=len(collected)))

    def _pick_folder(self) -> None:
        folder = ask_directory(
            self,
            title=self._t("dialog_select_folder"),
            initial_dir=_default_pictures_dir(),
            t=self._t,
        )
        if not folder:
            return
        collected = collect_images([folder])
        if not collected:
            messagebox.showwarning(self._t("app_name"), self._t("warn_no_images"))
            return
        merged = {p.resolve() for p in self._selected_files}
        merged.update(collected)
        self._selected_files = sorted(merged)
        self._update_source_label()
        self._log(self._t("log_added_folder", count=len(collected), folder=folder))

    def _clear_sources(self) -> None:
        self._selected_files = []
        self._update_source_label()
        self._log(self._t("log_cleared"))

    def _pick_output(self) -> None:
        initial = self._output_dir or _default_pictures_dir()
        folder = ask_directory(
            self,
            title=self._t("dialog_choose_dest"),
            initial_dir=initial,
            t=self._t,
        )
        if not folder:
            return
        self._output_dir = folder
        self.output_label.configure(text=str(self._output_dir))
        self._log(self._t("log_destination", path=self._output_dir))

    def _validate_before_start(self) -> str | None:
        if self._busy:
            return self._t("err_busy")
        if not self._selected_files:
            return self._t("err_no_photos")
        if self._output_dir is None:
            return self._t("err_no_dest")
        return None

    def _start_conversion(self) -> None:
        error = self._validate_before_start()
        if error:
            messagebox.showerror(self._t("app_name"), error)
            return

        fmt = self.format_var.get()
        quality = int(self.quality_var.get())
        overwrite = bool(self.overwrite_var.get())
        sources = list(self._selected_files)
        dest = self._output_dir
        assert dest is not None

        if not messagebox.askyesno(
            self._t("app_name"),
            self._t("confirm_convert", count=len(sources), fmt=fmt, dest=dest),
        ):
            return

        self._busy = True
        self._cancel.clear()
        self.convert_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress.set(0)
        self.status_label.configure(text=self._t("status_starting"))
        self._log(self._t("log_started", count=len(sources), fmt=fmt, quality=quality))

        def worker() -> None:
            def on_progress(current: int, total: int, name: str) -> None:
                self.after(0, lambda: self._ui_progress(current, total, name))

            summary = convert_many(
                sources,
                dest,
                fmt,
                quality=quality,
                overwrite=overwrite,
                progress=on_progress,
                cancel_flag=self._cancel.is_set,
            )
            self.after(0, lambda: self._ui_finished(summary))

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def _ui_progress(self, current: int, total: int, name: str) -> None:
        fraction = current / total if total else 0
        self.progress.set(fraction)
        self.status_label.configure(
            text=self._t("status_converting", current=current, total=total, name=name)
        )
        self._log(f"[{current}/{total}] {name}")

    def _ui_finished(self, summary) -> None:
        self._busy = False
        self.convert_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.progress.set(1.0 if summary.failed == 0 and summary.skipped == 0 else self.progress.get())

        msg = self._t(
            "done_summary",
            ok=summary.succeeded,
            failed=summary.failed,
            skipped=summary.skipped,
        )
        self.status_label.configure(text=msg)
        self._log(f"--- {msg} ---")

        for item in summary.results:
            if not item.success and item.error:
                self._log(self._t("error_prefix", error=item.error))

        name = self._t("app_name")
        if summary.failed and summary.succeeded == 0:
            messagebox.showerror(name, self._t("all_failed", msg=msg))
        elif summary.failed:
            messagebox.showwarning(name, msg)
        elif summary.skipped and summary.succeeded == 0:
            messagebox.showinfo(name, self._t("cancelled"))
        else:
            messagebox.showinfo(name, msg)

    def _cancel_conversion(self) -> None:
        if self._busy:
            self._cancel.set()
            self.status_label.configure(text=self._t("status_cancelling"))
            self._log(self._t("log_cancel"))

    def _on_close(self) -> None:
        if self._busy:
            if not messagebox.askyesno(self._t("app_name"), self._t("exit_busy")):
                return
            self._cancel.set()
        self.destroy()


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app = PhotoConverterApp()
    app.mainloop()

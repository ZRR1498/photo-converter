"""Explorer-style file/folder picker with real multi-select (Ctrl / Shift / drag)."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Callable, Literal

import customtkinter as ctk

from photo_converter.formats import INPUT_EXTENSIONS

Mode = Literal["files", "folder"]


def _is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in INPUT_EXTENSIONS


def _safe_listdir(directory: Path) -> tuple[list[Path], list[Path]]:
    dirs: list[Path] = []
    files: list[Path] = []
    try:
        entries = list(directory.iterdir())
    except (PermissionError, OSError):
        return [], []
    for entry in entries:
        try:
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                dirs.append(entry)
            elif _is_image(entry):
                files.append(entry)
        except (PermissionError, OSError):
            continue
    dirs.sort(key=lambda p: p.name.lower())
    files.sort(key=lambda p: p.name.lower())
    return dirs, files


def _human_size(num: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num} B"


class ExplorerDialog(ctk.CTkToplevel):
    """Modal explorer: navigate folders, multi-select photos like a file manager."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        title: str,
        initial_dir: Path,
        mode: Mode,
        t: Callable[..., str],
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.geometry("900x560")
        self.minsize(700, 420)
        self.transient(master)
        self.grab_set()
        self.focus_set()

        self._t = t
        self._mode: Mode = mode
        self._cwd = initial_dir.expanduser().resolve()
        if not self._cwd.is_dir():
            self._cwd = Path.home()

        self.result: list[Path] | None = None
        self._entries: list[tuple[str, Path]] = []  # display kind + path

        self._build()
        self._navigate(self._cwd)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Escape>", lambda _e: self._on_cancel())
        self.after(50, self._center_on_parent)

    def _center_on_parent(self) -> None:
        try:
            self.update_idletasks()
            px = self.master.winfo_rootx()
            py = self.master.winfo_rooty()
            pw = self.master.winfo_width()
            ph = self.master.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")
        except tk.TclError:
            pass

    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Sidebar places ---
        side = ctk.CTkFrame(self, width=180)
        side.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=(12, 6), pady=12)
        side.grid_propagate(False)
        ctk.CTkLabel(side, text=self._t("explorer_places"), font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=12, pady=(12, 8)
        )
        places = [
            ("explorer_home", Path.home()),
            ("explorer_pictures", self._pictures_dir()),
            ("explorer_desktop", Path.home() / "Desktop"),
            ("explorer_downloads", Path.home() / "Downloads"),
        ]
        # Russian common names as fallbacks
        for key, path in places:
            if key == "explorer_pictures" and not path.is_dir():
                alt = Path.home() / "Изображения"
                path = alt if alt.is_dir() else path
            if key == "explorer_desktop" and not path.is_dir():
                alt = Path.home() / "Рабочий стол"
                path = alt if alt.is_dir() else path
            if key == "explorer_downloads" and not path.is_dir():
                alt = Path.home() / "Загрузки"
                path = alt if alt.is_dir() else path
            btn = ctk.CTkButton(
                side,
                text=self._t(key),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                command=lambda p=path: self._navigate(p if p.is_dir() else Path.home()),
            )
            btn.pack(fill="x", padx=8, pady=2)

        # --- Toolbar ---
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=1, sticky="ew", padx=(6, 12), pady=(12, 4))
        toolbar.grid_columnconfigure(3, weight=1)

        self.btn_up = ctk.CTkButton(toolbar, text="↑", width=40, command=self._go_up)
        self.btn_up.grid(row=0, column=0, padx=(0, 4))
        self.btn_refresh = ctk.CTkButton(toolbar, text="↻", width=40, command=self._refresh)
        self.btn_refresh.grid(row=0, column=1, padx=4)

        ctk.CTkLabel(toolbar, text=self._t("explorer_path")).grid(row=0, column=2, padx=(8, 4))
        self.path_var = ctk.StringVar(value=str(self._cwd))
        self.path_entry = ctk.CTkEntry(toolbar, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=3, sticky="ew", padx=4)
        self.path_entry.bind("<Return>", lambda _e: self._go_path())
        ctk.CTkButton(toolbar, text=self._t("explorer_go"), width=70, command=self._go_path).grid(
            row=0, column=4, padx=(4, 0)
        )

        # --- List area (native Listbox = real explorer multi-select) ---
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=4)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Match CTk colors roughly
        bg = self._list_bg()
        fg = self._list_fg()
        sel = "#1f6aa5"

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED if self._mode == "files" else tk.BROWSE,
            activestyle="dotbox",
            font=("Segoe UI", 11) if self._is_windows() else ("DejaVu Sans", 11),
            bg=bg,
            fg=fg,
            selectbackground=sel,
            selectforeground="#ffffff",
            highlightthickness=0,
            borderwidth=0,
            relief="flat",
            exportselection=False,
        )
        scroll = ctk.CTkScrollbar(list_frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)

        self.listbox.bind("<Double-Button-1>", self._on_double_click)
        self.listbox.bind("<Return>", self._on_enter)
        self.listbox.bind("<BackSpace>", lambda _e: self._go_up())
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Control-a>", self._select_all_images)
        self.listbox.bind("<Control-A>", self._select_all_images)

        hint = ctk.CTkLabel(
            list_frame,
            text=self._t("explorer_hint_files" if self._mode == "files" else "explorer_hint_folder"),
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray65"),
            anchor="w",
        )
        hint.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))

        # --- Footer ---
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=1, sticky="ew", padx=(6, 12), pady=(4, 12))
        footer.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(footer, text="", anchor="w")
        self.status.grid(row=0, column=0, sticky="w")

        if self._mode == "files":
            ctk.CTkButton(
                footer,
                text=self._t("explorer_select_all"),
                width=140,
                fg_color=("gray70", "gray35"),
                hover_color=("gray55", "gray45"),
                command=lambda: self._select_all_images(),
            ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            footer,
            text=self._t("btn_cancel"),
            width=110,
            fg_color=("gray70", "gray35"),
            hover_color=("gray55", "gray45"),
            command=self._on_cancel,
        ).grid(row=0, column=2, padx=6)

        self.ok_btn = ctk.CTkButton(
            footer,
            text=self._t("explorer_open" if self._mode == "files" else "explorer_choose"),
            width=140,
            command=self._on_ok,
        )
        self.ok_btn.grid(row=0, column=3, padx=(6, 0))

    @staticmethod
    def _is_windows() -> bool:
        import platform

        return platform.system() == "Windows"

    def _list_bg(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#2b2b2b" if mode == "Dark" else "#f2f2f2"

    def _list_fg(self) -> str:
        mode = ctk.get_appearance_mode()
        return "#e8e8e8" if mode == "Dark" else "#1a1a1a"

    def _pictures_dir(self) -> Path:
        home = Path.home()
        for name in ("Pictures", "Images", "photos", "Photos", "Изображения"):
            candidate = home / name
            if candidate.is_dir():
                return candidate
        return home

    def _navigate(self, path: Path) -> None:
        path = path.expanduser()
        try:
            path = path.resolve()
        except OSError:
            return
        if not path.is_dir():
            return
        self._cwd = path
        self.path_var.set(str(self._cwd))
        self._populate()

    def _refresh(self) -> None:
        self._navigate(self._cwd)

    def _go_up(self) -> None:
        parent = self._cwd.parent
        if parent != self._cwd:
            self._navigate(parent)

    def _go_path(self) -> None:
        raw = self.path_var.get().strip()
        if not raw:
            return
        self._navigate(Path(raw))

    def _populate(self) -> None:
        self.listbox.delete(0, tk.END)
        self._entries.clear()

        dirs, files = _safe_listdir(self._cwd)

        if self._cwd.parent != self._cwd:
            self._entries.append(("up", self._cwd.parent))
            self.listbox.insert(tk.END, self._t("explorer_parent"))

        for d in dirs:
            self._entries.append(("dir", d))
            self.listbox.insert(tk.END, f"[DIR]  {d.name}")

        if self._mode == "files":
            for f in files:
                try:
                    size = _human_size(f.stat().st_size)
                except OSError:
                    size = "?"
                self._entries.append(("file", f))
                self.listbox.insert(tk.END, f"[IMG]  {f.name}    ({size})")
        else:
            # Folder mode: still show images (read-only cue) but selection targets folders.
            for f in files:
                self._entries.append(("file", f))
                self.listbox.insert(tk.END, f"[IMG]  {f.name}")

        self._update_status()
        try:
            self.listbox.focus_set()
        except tk.TclError:
            pass

    def _selected_indices(self) -> list[int]:
        return list(self.listbox.curselection())

    def _on_select(self, _event=None) -> None:
        self._update_status()

    def _update_status(self) -> None:
        idxs = self._selected_indices()
        if self._mode == "files":
            files = [self._entries[i][1] for i in idxs if self._entries[i][0] == "file"]
            self.status.configure(text=self._t("explorer_status_files", count=len(files)))
        else:
            if len(idxs) == 1 and self._entries[idxs[0]][0] in ("dir", "up"):
                name = self._entries[idxs[0]][1].name or str(self._entries[idxs[0]][1])
                self.status.configure(text=self._t("explorer_status_folder", name=name))
            else:
                self.status.configure(
                    text=self._t("explorer_status_folder", name=self._cwd.name or str(self._cwd))
                )

    def _select_all_images(self, _event=None):
        self.listbox.selection_clear(0, tk.END)
        for i, (kind, _) in enumerate(self._entries):
            if kind == "file":
                self.listbox.selection_set(i)
        self._update_status()
        return "break"

    def _on_double_click(self, _event=None) -> None:
        idxs = self._selected_indices()
        if not idxs:
            return
        kind, path = self._entries[idxs[0]]
        if kind in ("dir", "up"):
            self._navigate(path)
        elif kind == "file" and self._mode == "files":
            self._on_ok()

    def _on_enter(self, _event=None) -> None:
        idxs = self._selected_indices()
        if len(idxs) == 1 and self._entries[idxs[0]][0] in ("dir", "up"):
            self._navigate(self._entries[idxs[0]][1])
            return
        self._on_ok()

    def _on_ok(self) -> None:
        if self._mode == "files":
            idxs = self._selected_indices()
            files = [self._entries[i][1] for i in idxs if self._entries[i][0] == "file"]
            if not files:
                # If a single folder is highlighted, optionally enter it instead of closing.
                if len(idxs) == 1 and self._entries[idxs[0]][0] in ("dir", "up"):
                    self._navigate(self._entries[idxs[0]][1])
                    return
                self.status.configure(text=self._t("explorer_need_files"))
                return
            self.result = files
        else:
            idxs = self._selected_indices()
            if len(idxs) == 1 and self._entries[idxs[0]][0] == "dir":
                self.result = [self._entries[idxs[0]][1]]
            else:
                # Current directory
                self.result = [self._cwd]
        self.destroy()

    def _on_cancel(self) -> None:
        self.result = None
        self.destroy()


def ask_open_images(
    master: tk.Misc,
    *,
    title: str,
    initial_dir: Path,
    t: Callable[..., str],
) -> list[Path] | None:
    dialog = ExplorerDialog(master, title=title, initial_dir=initial_dir, mode="files", t=t)
    master.wait_window(dialog)
    return dialog.result


def ask_directory(
    master: tk.Misc,
    *,
    title: str,
    initial_dir: Path,
    t: Callable[..., str],
) -> Path | None:
    dialog = ExplorerDialog(master, title=title, initial_dir=initial_dir, mode="folder", t=t)
    master.wait_window(dialog)
    if not dialog.result:
        return None
    return dialog.result[0]

"""UI strings for English and Russian."""

from __future__ import annotations

import locale
from typing import Any

LANG_EN = "en"
LANG_RU = "ru"
LANG_CODES = (LANG_EN, LANG_RU)

LANG_DISPLAY = {
    LANG_EN: "English",
    LANG_RU: "Русский",
}

# Format-code → localized quality hint key suffix is handled via QUALITY_HINTS.
QUALITY_HINTS: dict[str, dict[str, str]] = {
    LANG_EN: {
        "PNG": "Lossless format — original pixel data preserved.",
        "TIFF": "Lossless format — original pixel data preserved.",
        "BMP": "Lossless format — original pixel data preserved.",
        "GIF": "Lossless format — original pixel data preserved.",
        "WEBP": "WEBP at quality 100 uses lossless mode.",
        "JPEG": "JPEG uses high quality (95) and 4:4:4 chroma (minimal loss).",
        "AVIF": "AVIF at quality 100 aims for near-lossless compression.",
        "ICO": "Best-effort quality preservation.",
        "_default": "Best-effort quality preservation.",
    },
    LANG_RU: {
        "PNG": "Формат без потерь — пиксели сохраняются как есть.",
        "TIFF": "Формат без потерь — пиксели сохраняются как есть.",
        "BMP": "Формат без потерь — пиксели сохраняются как есть.",
        "GIF": "Формат без потерь — пиксели сохраняются как есть.",
        "WEBP": "WEBP при качестве 100 сохраняется без потерь.",
        "JPEG": "JPEG: высокое качество (95) и цветность 4:4:4 (минимум потерь).",
        "AVIF": "AVIF при качестве 100 стремится к почти безпотерьному сжатию.",
        "ICO": "Максимально бережное сохранение качества.",
        "_default": "Максимально бережное сохранение качества.",
    },
}

STRINGS: dict[str, dict[str, str]] = {
    LANG_EN: {
        "app_title": "Photo Converter v{version}",
        "app_name": "Photo Converter",
        "subtitle": (
            "Select photos → choose output format → pick destination → convert.\n"
            "Originals are never modified."
        ),
        "heif_on": "HEIC / HEIF / AVIF support: enabled",
        "heif_off": "HEIC / HEIF support: unavailable (install pillow-heif)",
        "source_title": "Source photos",
        "no_files": "No files selected",
        "files_selected": "{count} file(s) selected",
        "btn_select_photos": "Select photos…",
        "btn_select_folder": "Select folder…",
        "btn_clear": "Clear",
        "output_title": "Output settings",
        "label_format": "Format:",
        "label_quality": "Quality:",
        "overwrite": "Overwrite existing files in destination",
        "label_save_to": "Save to:",
        "not_selected": "Not selected",
        "btn_choose_folder": "Choose folder…",
        "selected_files": "Selected files",
        "log": "Log",
        "empty_list": "(empty)",
        "ready": "Ready",
        "btn_cancel": "Cancel",
        "btn_convert": "Convert",
        "language": "Language:",
        "dialog_select_photos": "Select photos to convert",
        "dialog_select_folder": "Select folder with photos",
        "dialog_choose_dest": "Choose destination folder for converted photos",
        "filetype_images": "Images",
        "filetype_all": "All files",
        "warn_no_images": "No supported images found in that folder (including subfolders).",
        "log_added_picker": "Added {count} file(s) from picker.",
        "log_added_folder": "Added {count} file(s) from folder: {folder}",
        "log_cleared": "Selection cleared.",
        "log_destination": "Destination: {path}",
        "err_busy": "Conversion already in progress.",
        "err_no_photos": "Please select at least one photo.",
        "err_no_dest": "Please choose a destination folder.",
        "confirm_convert": (
            "Convert {count} file(s) to {fmt}\n"
            "and save into:\n{dest}\n\n"
            "Original files will not be modified. Continue?"
        ),
        "status_starting": "Starting…",
        "log_started": "--- Conversion started: {count} → {fmt} (q={quality}) ---",
        "status_converting": "Converting {current}/{total}: {name}",
        "done_summary": "Done. Success: {ok}, failed: {failed}, skipped: {skipped}",
        "all_failed": "All conversions failed.\n{msg}",
        "cancelled": "Conversion cancelled.",
        "status_cancelling": "Cancelling…",
        "log_cancel": "Cancel requested…",
        "exit_busy": "Conversion is running. Exit anyway?",
        "log_lang": "Language: {lang}",
        "error_prefix": "ERROR: {error}",
        "explorer_places": "Places",
        "explorer_home": "Home",
        "explorer_pictures": "Pictures",
        "explorer_desktop": "Desktop",
        "explorer_downloads": "Downloads",
        "explorer_path": "Path:",
        "explorer_go": "Go",
        "explorer_parent": "⬆  .. (parent folder)",
        "explorer_hint_files": "Tip: Ctrl+click / Shift+click / drag to select many photos. Ctrl+A — all images. Double-click a folder to open it.",
        "explorer_hint_folder": "Select a folder (or stay in the current one) and press Choose. Double-click a folder to open it.",
        "explorer_select_all": "Select all images",
        "explorer_open": "Add selected",
        "explorer_choose": "Choose this folder",
        "explorer_status_files": "Selected images: {count}",
        "explorer_status_folder": "Folder: {name}",
        "explorer_need_files": "Select at least one image (folders open on double-click).",
    },
    LANG_RU: {
        "app_title": "Конвертер фото v{version}",
        "app_name": "Конвертер фото",
        "subtitle": (
            "Выберите фото → формат → папку сохранения → конвертировать.\n"
            "Исходные файлы не изменяются."
        ),
        "heif_on": "Поддержка HEIC / HEIF / AVIF: включена",
        "heif_off": "Поддержка HEIC / HEIF: недоступна (установите pillow-heif)",
        "source_title": "Исходные фото",
        "no_files": "Файлы не выбраны",
        "files_selected": "Выбрано файлов: {count}",
        "btn_select_photos": "Выбрать фото…",
        "btn_select_folder": "Выбрать папку…",
        "btn_clear": "Очистить",
        "output_title": "Параметры вывода",
        "label_format": "Формат:",
        "label_quality": "Качество:",
        "overwrite": "Перезаписывать существующие файлы в папке назначения",
        "label_save_to": "Сохранить в:",
        "not_selected": "Не выбрано",
        "btn_choose_folder": "Выбрать папку…",
        "selected_files": "Выбранные файлы",
        "log": "Журнал",
        "empty_list": "(пусто)",
        "ready": "Готово",
        "btn_cancel": "Отмена",
        "btn_convert": "Конвертировать",
        "language": "Язык:",
        "dialog_select_photos": "Выберите фотографии для конвертации",
        "dialog_select_folder": "Выберите папку с фотографиями",
        "dialog_choose_dest": "Выберите папку для сохранения конвертированных фото",
        "filetype_images": "Изображения",
        "filetype_all": "Все файлы",
        "warn_no_images": "В этой папке (включая подпапки) нет поддерживаемых изображений.",
        "log_added_picker": "Добавлено файлов из диалога: {count}.",
        "log_added_folder": "Добавлено файлов из папки: {count} — {folder}",
        "log_cleared": "Выбор очищен.",
        "log_destination": "Папка назначения: {path}",
        "err_busy": "Конвертация уже выполняется.",
        "err_no_photos": "Выберите хотя бы одну фотографию.",
        "err_no_dest": "Выберите папку для сохранения.",
        "confirm_convert": (
            "Конвертировать {count} файл(ов) в {fmt}\n"
            "и сохранить в:\n{dest}\n\n"
            "Исходные файлы не будут изменены. Продолжить?"
        ),
        "status_starting": "Запуск…",
        "log_started": "--- Конвертация начата: {count} → {fmt} (q={quality}) ---",
        "status_converting": "Конвертация {current}/{total}: {name}",
        "done_summary": "Готово. Успешно: {ok}, ошибок: {failed}, пропущено: {skipped}",
        "all_failed": "Все конвертации завершились ошибкой.\n{msg}",
        "cancelled": "Конвертация отменена.",
        "status_cancelling": "Отмена…",
        "log_cancel": "Запрошена отмена…",
        "exit_busy": "Идёт конвертация. Выйти всё равно?",
        "log_lang": "Язык: {lang}",
        "error_prefix": "ОШИБКА: {error}",
        "explorer_places": "Места",
        "explorer_home": "Домашняя",
        "explorer_pictures": "Изображения",
        "explorer_desktop": "Рабочий стол",
        "explorer_downloads": "Загрузки",
        "explorer_path": "Путь:",
        "explorer_go": "Перейти",
        "explorer_parent": "⬆  .. (наверх)",
        "explorer_hint_files": "Совет: Ctrl+клик / Shift+клик / протяжка мышью — выбрать много фото. Ctrl+A — все. Двойной клик по папке — открыть.",
        "explorer_hint_folder": "Выберите папку (или оставьте текущую) и нажмите «Выбрать». Двойной клик по папке — открыть.",
        "explorer_select_all": "Выделить все фото",
        "explorer_open": "Добавить выбранные",
        "explorer_choose": "Выбрать эту папку",
        "explorer_status_files": "Выбрано изображений: {count}",
        "explorer_status_folder": "Папка: {name}",
        "explorer_need_files": "Выберите хотя бы одно изображение (папки открываются двойным кликом).",
    },
}


def detect_system_lang() -> str:
    """Prefer Russian when the OS locale is Russian; otherwise English."""
    try:
        loc = locale.getdefaultlocale()[0] or ""
    except Exception:  # noqa: BLE001
        loc = ""
    if loc.lower().startswith("ru"):
        return LANG_RU
    return LANG_EN


def quality_hint(lang: str, format_label: str) -> str:
    table = QUALITY_HINTS.get(lang, QUALITY_HINTS[LANG_EN])
    return table.get(format_label, table["_default"])


class I18n:
    """Tiny translator with live language switching."""

    def __init__(self, lang: str | None = None) -> None:
        self.lang = lang if lang in LANG_CODES else detect_system_lang()

    def set_lang(self, lang: str) -> None:
        if lang not in LANG_CODES:
            raise ValueError(f"Unsupported language: {lang}")
        self.lang = lang

    def t(self, key: str, **kwargs: Any) -> str:
        table = STRINGS.get(self.lang, STRINGS[LANG_EN])
        template = table.get(key) or STRINGS[LANG_EN].get(key, key)
        if kwargs:
            return template.format(**kwargs)
        return template

    def hint(self, format_label: str) -> str:
        return quality_hint(self.lang, format_label)

    @property
    def display_name(self) -> str:
        return LANG_DISPLAY.get(self.lang, self.lang)

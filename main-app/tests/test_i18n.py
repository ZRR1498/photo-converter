"""Tests for RU/EN localization."""

from __future__ import annotations

from photo_converter.i18n import LANG_EN, LANG_RU, STRINGS, I18n, quality_hint


def test_both_languages_have_same_keys() -> None:
    assert set(STRINGS[LANG_EN]) == set(STRINGS[LANG_RU])


def test_switch_language() -> None:
    i18n = I18n(LANG_EN)
    assert "Convert" in i18n.t("btn_convert")
    i18n.set_lang(LANG_RU)
    assert "Конвертировать" in i18n.t("btn_convert")
    assert "файлов" in i18n.t("files_selected", count=3)


def test_quality_hints_localized() -> None:
    assert "Lossless" in quality_hint(LANG_EN, "PNG")
    assert "без потерь" in quality_hint(LANG_RU, "PNG").lower()
    assert "JPEG" in quality_hint(LANG_EN, "JPEG")
    assert "JPEG" in quality_hint(LANG_RU, "JPEG")


def test_formatting() -> None:
    i18n = I18n(LANG_RU)
    msg = i18n.t("done_summary", ok=2, failed=1, skipped=0)
    assert "2" in msg and "1" in msg

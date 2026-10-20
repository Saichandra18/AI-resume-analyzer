"""Tests for tools/fix_mojibake.py (repairs double-encoded UTF-8)."""

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "fix_mojibake",
    Path(__file__).resolve().parents[1] / "tools" / "fix_mojibake.py",
)
fix_mojibake = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fix_mojibake)


def _mangle(text):
    """Simulate the damage: UTF-8 bytes shown as Windows-1252."""
    out = []
    for byte in text.encode("utf-8"):
        try:
            out.append(bytes([byte]).decode("cp1252"))
        except UnicodeDecodeError:
            out.append(chr(byte))
    return "".join(out)


def test_repairs_the_symbols_seen_in_the_app():
    for good in ("\u2713", "\u25cf", "\u25cb", "\u2022", "\u2014", "\u2013"):
        repaired, count = fix_mojibake.fix_text(_mangle(good))

        assert repaired == good
        assert count == 1


def test_repairs_inside_real_code():
    broken = 'icon.textContent = "' + _mangle("\u2713") + '"; // ' + _mangle("\u2014") + " done"

    repaired, count = fix_mojibake.fix_text(broken)

    assert repaired == 'icon.textContent = "\u2713"; // \u2014 done'
    assert count == 2


def test_clean_text_is_left_unchanged():
    text = 'Caf\u00e9 \u2713 \u2022 \u2014 normal "quotes" and \u00e2 alone'

    assert fix_mojibake.fix_text(text) == (text, 0)


def test_repair_is_idempotent():
    once, _ = fix_mojibake.fix_text(_mangle("\u2713 done"))

    assert fix_mojibake.fix_text(once) == (once, 0)

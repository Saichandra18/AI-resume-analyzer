"""Repair double-encoded UTF-8 text ("mojibake") in project files.

Symptom: the browser shows "âœ“" instead of a check mark, "â€¢" instead of
a bullet, "â€”" instead of a dash.  It happens when a UTF-8 file is read as
Windows-1252 (for example by PowerShell's Get-Content/Set-Content without
-Encoding UTF8) and then saved again as UTF-8.

Usage (run from the project root):

    python tools/fix_mojibake.py --check     # only report what would change
    python tools/fix_mojibake.py             # repair the frontend files
    python tools/fix_mojibake.py path1 path2 # repair specific files/folders

Line endings and a leading BOM are preserved.  Commit first so git is your
backup.
"""

import re
import sys
from pathlib import Path

DEFAULT_TARGETS = [
    "frontend/static/js",
    "frontend/static/css",
    "frontend/templates",
]
EXTENSIONS = {".js", ".css", ".html", ".htm", ".txt", ".md"}


def _char_for_byte(value):
    """The character Windows-1252 shows for a byte (latin-1 for gaps)."""
    try:
        return bytes([value]).decode("cp1252")
    except UnicodeDecodeError:
        return chr(value)


def _byte_for_char(char):
    try:
        return char.encode("cp1252")[0]
    except UnicodeEncodeError:
        if ord(char) < 256:
            return ord(char)
        raise


_CONTINUATION = "".join(_char_for_byte(b) for b in range(0x80, 0xC0))
_LEAD2 = "".join(_char_for_byte(b) for b in range(0xC2, 0xE0))
_LEAD3 = "".join(_char_for_byte(b) for b in range(0xE0, 0xF0))
_LEAD4 = "".join(_char_for_byte(b) for b in range(0xF0, 0xF5))

_PATTERN = re.compile(
    "(?:"
    f"[{re.escape(_LEAD4)}][{re.escape(_CONTINUATION)}]{{3}}"
    f"|[{re.escape(_LEAD3)}][{re.escape(_CONTINUATION)}]{{2}}"
    f"|[{re.escape(_LEAD2)}][{re.escape(_CONTINUATION)}]"
    ")"
)


def fix_text(text):
    """Return (repaired_text, number_of_repairs)."""
    count = 0

    def repair(match):
        nonlocal count
        chunk = match.group(0)
        try:
            repaired = bytes(_byte_for_char(c) for c in chunk).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return chunk
        count += 1
        return repaired

    return _PATTERN.sub(repair, text), count


def _files(targets):
    for target in targets:
        path = Path(target)
        if path.is_file():
            yield path
        elif path.is_dir():
            for item in sorted(path.rglob("*")):
                if item.is_file() and item.suffix.lower() in EXTENSIONS:
                    yield item


def main(argv):
    check_only = "--check" in argv
    targets = [a for a in argv if not a.startswith("--")] or DEFAULT_TARGETS
    total = 0

    for path in _files(targets):
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            print(f"skip (not UTF-8): {path}")
            continue

        fixed, count = fix_text(text)

        if not count:
            continue

        total += count
        print(f"{'would fix' if check_only else 'fixed'} {count:3d} in {path}")

        if not check_only:
            path.write_bytes(fixed.encode("utf-8"))

    print(f"\n{total} repair(s){' (nothing written: --check)' if check_only else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

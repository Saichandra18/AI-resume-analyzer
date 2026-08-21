import pytest

from app.services.resume_parser import extract_resume_text


def test_unsupported_file_format():
    with pytest.raises(ValueError):
        extract_resume_text("resume.txt")
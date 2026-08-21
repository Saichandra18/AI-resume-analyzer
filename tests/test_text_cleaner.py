from app.services.text_cleaner import clean_resume_text


def test_clean_resume_text():
    text = "Python    SQL\n\n\n\nMachine Learning"

    result = clean_resume_text(text)

    assert result == "Python SQL\n\nMachine Learning"
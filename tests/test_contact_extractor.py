from app.contact_extractor import extract_email, extract_phone


def test_extract_email():
    text = "Contact me at sai@example.com"

    email = extract_email(text)

    assert email == "sai@example.com"


def test_extract_email_when_missing():
    text = "No email address is available."

    email = extract_email(text)

    assert email is None


def test_extract_phone():
    text = "Phone: 9876543210"

    phone = extract_phone(text)

    assert phone == "9876543210"


def test_extract_indian_phone_with_country_code():
    text = "Phone: +91 9876543210"

    phone = extract_phone(text)

    assert phone == "+91 9876543210"


def test_extract_phone_when_missing():
    text = "No phone number is available."

    phone = extract_phone(text)

    assert phone is None
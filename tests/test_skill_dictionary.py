from app.skill_dictionary import SKILL_DICTIONARY


def test_skill_dictionary_exists():
    assert isinstance(SKILL_DICTIONARY, dict)


def test_programming_languages_exist():
    assert "programming_languages" in SKILL_DICTIONARY


def test_python_is_in_dictionary():
    assert "Python" in SKILL_DICTIONARY["programming_languages"]


def test_sql_is_in_dictionary():
    assert "SQL" in SKILL_DICTIONARY["programming_languages"]


def test_power_bi_is_in_dictionary():
    assert "Power BI" in SKILL_DICTIONARY["data_analysis"]
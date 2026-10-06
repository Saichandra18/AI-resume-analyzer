from app.rewrite_validator import validate_rewrite


def test_validate_rewrite_accepts_grounded_rewrite():
    result = validate_rewrite(
        "Built a Flask app.",
        "Developed a Flask application.",
    )

    assert result["grounding_status"] == "grounded"
    assert result["meaning_preserved"] is True
    assert result["unsupported_claims"] == []


def test_validate_rewrite_detects_new_number():
    result = validate_rewrite(
        "Built a Flask app.",
        "Developed a Flask application used by 50000 users.",
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False
    assert any(
        "50000" in claim
        for claim in result["unsupported_claims"]
    )


def test_validate_rewrite_detects_new_percentage():
    result = validate_rewrite(
        "Improved the application.",
        "Improved the application by 40%.",
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "40%" in claim
        for claim in result["unsupported_claims"]
    )


def test_validate_rewrite_detects_new_technical_term():
    result = validate_rewrite(
        "Built a Flask application.",
        "Built a Flask application using Docker.",
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "docker" in claim
        for claim in result["unsupported_claims"]
    )


def test_validate_rewrite_accepts_existing_technical_term():
    result = validate_rewrite(
        "Built a Flask application.",
        "Developed a Flask application.",
    )

    assert result["grounding_status"] == "grounded"


def test_validate_rewrite_handles_empty_original():
    result = validate_rewrite(
        "",
        "Developed a Flask application.",
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False


def test_validate_rewrite_handles_empty_rewritten():
    result = validate_rewrite(
        "Built a Flask application.",
        "",
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False

def test_validate_rewrite_accepts_new_term_supported_by_resume_evidence():
    result = validate_rewrite(
        "Built a machine learning model using Python.",
        "Built a machine learning model using Python and PySpark.",
        evidence_text="""
        Skills:
        Python
        PySpark

        Experience:
        Used PySpark for data processing.
        """,
    )

    assert result["grounding_status"] == "grounded"
    assert result["meaning_preserved"] is True
    assert result["unsupported_claims"] == []


def test_validate_rewrite_rejects_new_term_not_supported_by_resume_evidence():
    result = validate_rewrite(
        "Built a machine learning model using Python.",
        "Built a machine learning model using Python and Kubernetes.",
        evidence_text="""
        Skills:
        Python
        PySpark
        """,
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False
    assert any(
        "kubernetes" in claim
        for claim in result["unsupported_claims"]
    )


def test_validate_rewrite_accepts_new_number_supported_by_resume_evidence():
    result = validate_rewrite(
        "Improved the application.",
        "Improved the application to support 500 users.",
        evidence_text="""
        Project:
        Developed an application that supported 500 users.
        """,
    )

    assert result["grounding_status"] == "grounded"
    assert result["meaning_preserved"] is True
    assert result["unsupported_claims"] == []


def test_validate_rewrite_rejects_new_number_not_supported_by_resume_evidence():
    result = validate_rewrite(
        "Improved the application.",
        "Improved the application to support 50000 users.",
        evidence_text="""
        Project:
        Developed an application that supported 500 users.
        """,
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False
    assert any(
        "50000" in claim
        for claim in result["unsupported_claims"]
    )
def test_validate_rewrite_detects_unsupported_langchain():
    result = validate_rewrite(
        "Built an AI application using Python.",
        "Built an AI application using Python and LangChain.",
        evidence_text="""
        Skills:
        Python
        SQL
        """,
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "langchain" in claim
        for claim in result["unsupported_claims"]
    )


def test_validate_rewrite_detects_unsupported_pyspark():
    result = validate_rewrite(
        "Performed data analysis using Python.",
        "Performed data analysis using Python and PySpark.",
        evidence_text="""
        Skills:
        Python
        SQL
        """,
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "pyspark" in claim
        for claim in result["unsupported_claims"]
    )


def test_validate_rewrite_detects_unsupported_xgboost():
    result = validate_rewrite(
        "Developed a machine learning model.",
        "Developed a machine learning model using XGBoost.",
        evidence_text="""
        Skills:
        Python
        Scikit-learn
        """,
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "xgboost" in claim
        for claim in result["unsupported_claims"]
    )
def test_validate_rewrite_detects_unsupported_technical_looking_term():
    result = validate_rewrite(
        "Built an AI application using Python.",
        "Built an AI application using Python and VectorDBX.",
        evidence_text="""
        Skills:
        Python
        SQL
        """,
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "vectordbx" in claim
        for claim in result["unsupported_claims"]
    )

def test_validate_rewrite_does_not_flag_normal_camel_case_word():
    result = validate_rewrite(
        "Worked with the HumanResources team.",
        "Worked closely with the HumanResources team.",
        evidence_text="",
    )

    assert result["grounding_status"] == "grounded"
    assert result["unsupported_claims"] == []

def test_validate_rewrite_does_not_flag_common_proper_name():
    result = validate_rewrite(
        "Collaborated with Microsoft.",
        "Collaborated closely with Microsoft.",
        evidence_text="",
    )

    assert result["grounding_status"] == "grounded"
    assert result["unsupported_claims"] == []

def test_validate_rewrite_accepts_existing_camel_case_technical_term():
    result = validate_rewrite(
        "Built an application using VectorDBX.",
        "Built a scalable application using VectorDBX.",
        evidence_text="",
    )

    assert result["grounding_status"] == "grounded"
    assert result["unsupported_claims"] == []

def test_validate_rewrite_does_not_flag_hyphenated_descriptive_word():
    result = validate_rewrite(
        "Reviewed generated content.",
        "Reviewed generated content using a quality-focused evaluation.",
        evidence_text="",
    )

    assert result["grounding_status"] == "grounded"
    assert result["unsupported_claims"] == []

def test_validate_rewrite_does_not_flag_service_level():
    result = validate_rewrite(
        "Maintained quality benchmarks.",
        "Maintained quality benchmarks under defined service-level agreements.",
        evidence_text="",
    )

    assert result["grounding_status"] == "grounded"
    assert result["unsupported_claims"] == []


def test_validate_rewrite_does_not_flag_nlp_based():
    result = validate_rewrite(
        "Worked on language processing tasks.",
        "Worked on NLP-based language processing tasks.",
        evidence_text="",
    )

    assert result["grounding_status"] == "grounded"
    assert result["unsupported_claims"] == []


def test_validator_flags_unsupported_consistency_claim():
    result = validate_rewrite(
        original="Maintained productivity and quality benchmarks.",
        rewritten=(
            "Consistently met productivity and quality requirements."
        ),
    )

    assert result["grounding_status"] == "needs_review"
    assert any(
        "consistently met" in claim
        for claim in result["unsupported_claims"]
    )
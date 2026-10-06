"""Deterministic evaluation cases for the RAG subsystem."""


class RAGEvaluationDataset:
    """Provide deterministic RAG retrieval evaluation cases."""

    CASES = (
        {
            "case_id": "python_backend",
            "description": "Python backend development",
            "query": "Python backend development",
            "relevant_chunk_ids": (
                "python-backend",
                "flask-api",
            ),
            "k": 3,
            "minimum_recall": 0.5,
            "minimum_precision": 0.33,
            "minimum_mrr": 0.5,
        },
        {
            "case_id": "flask_api",
            "description": "Flask REST API development",
            "query": "Flask REST API",
            "relevant_chunk_ids": (
                "flask-api",
            ),
            "k": 3,
            "minimum_recall": 1.0,
            "minimum_precision": 0.33,
            "minimum_mrr": 0.5,
        },
        {
            "case_id": "machine_learning",
            "description": "Machine learning experience",
            "query": "machine learning models",
            "relevant_chunk_ids": (
                "machine-learning",
            ),
            "k": 3,
            "minimum_recall": 1.0,
            "minimum_precision": 0.33,
            "minimum_mrr": 0.5,
        },
        {
            "case_id": "cloud_platform",
            "description": "Cloud platform experience",
            "query": "AWS cloud deployment",
            "relevant_chunk_ids": (
                "cloud-deployment",
            ),
            "k": 3,
            "minimum_recall": 1.0,
            "minimum_precision": 0.33,
            "minimum_mrr": 0.5,
        },
        {
            "case_id": "irrelevant_query",
            "description": "No relevant knowledge",
            "query": "quantum computing research",
            "relevant_chunk_ids": (),
            "k": 3,
            "minimum_recall": 0.0,
            "minimum_precision": 0.0,
            "minimum_mrr": 0.0,
        },
    )

    @classmethod
    def all(cls):
        """Return all evaluation cases."""

        return [
            dict(case)
            for case in cls.CASES
        ]

    @classmethod
    def get(cls, case_id):
        """Return one evaluation case by ID."""

        if not isinstance(case_id, str):
            raise TypeError(
                "case_id must be a string."
            )

        for case in cls.CASES:
            if case["case_id"] == case_id:
                return dict(case)

        raise KeyError(
            f"Unknown evaluation case: {case_id}"
        )

    @classmethod
    def count(cls):
        """Return the number of evaluation cases."""

        return len(cls.CASES)
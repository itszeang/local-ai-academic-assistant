from app.common.types import GenerationMode
from app.llm.query_classifier import QueryClassifier


def test_classifier_prefers_explicit_qa_mode() -> None:
    classifier = QueryClassifier()

    assert classifier.classify("What is the main finding?") == GenerationMode.QA


def test_classifier_detects_summary_intent() -> None:
    classifier = QueryClassifier()

    assert classifier.classify("Summarize this article") == GenerationMode.SUMMARIZATION


def test_classifier_detects_argument_intent() -> None:
    classifier = QueryClassifier()

    assert classifier.classify("Build an argument for this thesis") == GenerationMode.ARGUMENT_BUILDER


def test_classifier_detects_literature_review_intent() -> None:
    classifier = QueryClassifier()

    assert classifier.classify("Write a literature review about motivation") == GenerationMode.LITERATURE_REVIEW

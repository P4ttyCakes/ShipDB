"""Unit tests for the TF-IDF completion detector in ai_agent.py and a regression
sweep over the surrounding AIAgentService methods that share the module.
"""
import pytest

from backend.app.services import ai_agent
from backend.app.services.ai_agent import (
    AIAgentService,
    _tokenize,
    _build_idf,
    _tfidf_vector,
    _cosine_similarity,
)


def make_agent() -> AIAgentService:
    """Construct an AIAgentService without running __init__ (which requires a live API key)."""
    return AIAgentService.__new__(AIAgentService)


# ---- module-level TF-IDF helpers ----

def test_tokenize_lowercases_and_strips_stopwords():
    assert _tokenize("Perfect! I have ENOUGH information.") == ["perfect", "have", "enough", "information"]


def test_tokenize_empty_string():
    assert _tokenize("") == []


def test_tokenize_punctuation_only():
    assert _tokenize("!!! ??? ...") == []


def test_build_idf_known_term_gets_lower_weight_than_rare_term():
    docs = [["alpha", "beta"], ["alpha", "gamma"], ["alpha", "delta"]]
    idf = _build_idf(docs)
    # "alpha" appears in all docs -> lower idf than "beta" which appears in only one
    assert idf["alpha"] < idf["beta"]


def test_tfidf_vector_empty_tokens_returns_empty_vector():
    assert _tfidf_vector([], {"a": 1.0}) == {}


def test_cosine_similarity_identical_vectors_is_one():
    vec = {"a": 1.0, "b": 2.0}
    assert _cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_similarity_disjoint_vectors_is_zero():
    assert _cosine_similarity({"a": 1.0}, {"b": 1.0}) == 0.0


def test_cosine_similarity_empty_vector_is_zero():
    assert _cosine_similarity({}, {"a": 1.0}) == 0.0
    assert _cosine_similarity({"a": 1.0}, {}) == 0.0


# ---- _detect_completion_phrases behavior ----

@pytest.mark.parametrize("text", [
    "Perfect! I have enough information to create your database design.",
    "Great! I now have everything I need to design your database.",
    "All set, I can build this schema now.",
    "Got it, that gives me everything I need to design your database.",
    "Great, I now have all the details required to build this out.",
])
def test_detects_completion_signals(text):
    agent = make_agent()
    assert agent._detect_completion_phrases(text) is True


@pytest.mark.parametrize("text", [
    "What other features does your business need?",
    "Can you tell me more about your payment flow?",
    "Do you also want to track inventory locations?",
    "How many admins will use this system?",
    "Describe and explain your business.",
])
def test_does_not_flag_ordinary_questions(text):
    agent = make_agent()
    assert agent._detect_completion_phrases(text) is False


def test_empty_or_whitespace_text_is_not_complete():
    agent = make_agent()
    assert agent._detect_completion_phrases("") is False
    assert agent._detect_completion_phrases("   ") is False


def test_completion_detection_is_called_from_next_turn(monkeypatch):
    """next_turn() should mark done=True when the model's text matches via TF-IDF
    even if it didn't set done=true itself, preserving prior substring-matcher behavior."""
    agent = make_agent()
    agent._sessions = {}
    agent._lock = __import__("threading").Lock()
    agent._sessions["s1"] = {
        "history": [{"role": "assistant", "content": "Describe your business."}],
        "partial_spec": {},
        "done": False,
        "project_id": None,
    }

    monkeypatch.setattr(
        agent,
        "_call_model",
        lambda history, user_msg: {
            "next_question": "Great, I now have all the details required to build this out.",
            "done": False,
            "partial_spec": {"app_type": "Bakery", "db_type": "postgresql", "entities": []},
        },
    )

    result = agent.next_turn("s1", "We sell bread and pastries.")
    assert result["done"] is True


# ---- regression checks for neighboring methods (unaffected by this change) ----

def test_merge_partial_merges_nested_dicts():
    agent = make_agent()
    base = {"app_type": "Store", "entities": []}
    incoming = {"db_type": "postgresql"}
    merged = agent._merge_partial(dict(base), incoming)
    assert merged == {"app_type": "Store", "entities": [], "db_type": "postgresql"}


def test_merge_entities_updates_existing_and_adds_new():
    agent = make_agent()
    base_entities = [{"name": "users", "fields": [{"name": "id", "type": "uuid"}]}]
    incoming_entities = [
        {"name": "users", "fields": [{"name": "email", "type": "string"}]},
        {"name": "orders", "fields": [{"name": "id", "type": "uuid"}]},
    ]
    merged = agent._merge_entities(base_entities, incoming_entities)
    names = {e["name"] for e in merged}
    assert names == {"users", "orders"}
    users_entity = next(e for e in merged if e["name"] == "users")
    field_names = {f["name"] for f in users_entity["fields"]}
    assert field_names == {"id", "email"}


def test_validate_complete_spec_accepts_well_formed_spec():
    agent = make_agent()
    spec = {
        "app_type": "Store",
        "db_type": "postgresql",
        "entities": [{"name": "users", "fields": [{"name": "id", "type": "uuid"}]}],
    }
    assert agent._validate_complete_spec(spec) is True


def test_validate_complete_spec_rejects_missing_entities():
    agent = make_agent()
    spec = {"app_type": "Store", "db_type": "postgresql", "entities": []}
    assert agent._validate_complete_spec(spec) is False


def test_parse_json_response_extracts_json_from_surrounding_text():
    agent = make_agent()
    text = 'Sure thing! {"next_question": "ok", "done": false, "partial_spec": {}} Thanks.'
    parsed = agent._parse_json_response(text)
    assert parsed == {"next_question": "ok", "done": False, "partial_spec": {}}


def test_to_anthropic_messages_filters_unknown_roles():
    agent = make_agent()
    history = [
        {"role": "user", "content": "hi"},
        {"role": "system", "content": "ignored"},
        {"role": "assistant", "content": "hello"},
    ]
    msgs = agent._to_anthropic_messages(history)
    assert msgs == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]

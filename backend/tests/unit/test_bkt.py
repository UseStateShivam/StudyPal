import pytest
from app.ml.learner.bkt import BayesianKnowledgeTracer


def test_bkt_parameter_validation():
    # Valid parameters
    bkt = BayesianKnowledgeTracer(p_l0=0.2, p_t=0.15, p_g=0.25, p_s=0.10)
    assert bkt.p_l0 == 0.2

    # Invalid parameter should raise ValueError
    with pytest.raises(ValueError):
        BayesianKnowledgeTracer(p_l0=1.5)


def test_bkt_correct_response_increases_mastery():
    bkt = BayesianKnowledgeTracer(p_l0=0.2, p_t=0.15, p_g=0.25, p_s=0.10)
    prior = 0.2
    next_m = bkt.compute_next_mastery(prior, is_correct=True)
    # Mastery should increase after answering correctly
    assert next_m > prior
    assert next_m <= 1.0


def test_bkt_incorrect_response_decreases_mastery():
    bkt = BayesianKnowledgeTracer(p_l0=0.5, p_t=0.05, p_g=0.25, p_s=0.10)
    prior = 0.5
    next_m = bkt.compute_next_mastery(prior, is_correct=False)
    # Mastery should decrease after answering incorrectly
    assert next_m < prior
    assert next_m >= 0.0


def test_bkt_repeated_correct_converges_to_high_mastery():
    bkt = BayesianKnowledgeTracer(p_l0=0.1, p_t=0.15, p_g=0.2, p_s=0.1)
    m = 0.1
    for _ in range(10):
        m = bkt.compute_next_mastery(m, is_correct=True)
    assert m > 0.90


def test_bkt_probability_bounds_clamping():
    bkt = BayesianKnowledgeTracer(p_l0=0.0, p_t=0.0, p_g=0.0, p_s=0.0)
    # Even in degenerate parameter cases, output must remain safe
    val = bkt.compute_next_mastery(0.0, is_correct=False)
    assert 0.001 <= val <= 0.999

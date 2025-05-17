from learning_recommender.recommender.rule_based import compute_mastery, recommend_next_topics

def test_compute_mastery_basic():
    mastery = compute_mastery(quiz_score=80, time_spent=30, revisit_count=2)
    assert 0 <= mastery <= 1

def test_compute_mastery_perfect_score():
    mastery = compute_mastery(quiz_score=100, time_spent=60, revisit_count=3)
    assert mastery == 1.0

def test_compute_mastery_zero_score():
    mastery = compute_mastery(quiz_score=0, time_spent=0, revisit_count=0)
    assert mastery == 0.0

def test_compute_mastery_excessive_values():
    # Test with values above the optimal thresholds
    mastery = compute_mastery(quiz_score=120, time_spent=120, revisit_count=5)
    assert 0 <= mastery <= 1

def test_compute_mastery_weighted_average():
    # Test with specific values to verify the weighted average calculation
    mastery = compute_mastery(quiz_score=80, time_spent=30, revisit_count=2)
    expected = (0.5 * 0.8 + 0.3 * 0.5 + 0.2 * 0.67)  # 0.8 for quiz, 0.5 for time, 0.67 for revisits
    assert abs(mastery - expected) < 0.001  # Allow for small floating-point differences

def test_recommend_next_topics_initial():
    user_mastery = {}
    recs = recommend_next_topics(user_mastery)
    assert "Programming Basics" in recs
    assert len(recs) == 1

def test_recommend_next_topics_after_basics():
    user_mastery = {"Programming Basics": 0.8}
    recs = recommend_next_topics(user_mastery)
    assert set(recs) == {"Data Structures", "OOP", "Databases"}

def test_recommend_next_topics_after_data_structures():
    user_mastery = {"Programming Basics": 0.8, "Data Structures": 0.8}
    recs = recommend_next_topics(user_mastery)
    assert "Algorithms" in recs
    assert "Operating Systems" in recs

def test_recommend_next_topics_all_mastered():
    user_mastery = {t: 1.0 for t in [
        "Programming Basics", "Data Structures", "Algorithms", "OOP", "Databases", "Operating Systems"
    ]}
    recs = recommend_next_topics(user_mastery)
    assert recs == []

def test_compute_mastery_negative_values():
    mastery = compute_mastery(quiz_score=-10, time_spent=-5, revisit_count=-1)
    assert mastery == 0.0

def test_compute_mastery_large_values():
    mastery = compute_mastery(quiz_score=1000, time_spent=1000, revisit_count=100)
    assert 0.99 < mastery <= 1.0

def test_recommend_next_topics_custom_threshold():
    user_mastery = {"Programming Basics": 0.6}
    recs = recommend_next_topics(user_mastery, threshold=0.5)
    assert "Data Structures" in recs
    assert "Programming Basics" not in recs

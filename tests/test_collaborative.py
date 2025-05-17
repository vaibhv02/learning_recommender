import pytest
from learning_recommender.recommender.collaborative import CollaborativeFilteringRecommender

@pytest.fixture
def sample_user_topic_matrix():
    return {
        "user1": {
            "Programming Basics": 0.9,
            "Data Structures": 0.8,
            "Algorithms": 0.7,
            "OOP": 0.6,
            "Databases": 0.5
        },
        "user2": {
            "Programming Basics": 0.8,
            "Data Structures": 0.7,
            "Algorithms": 0.6,
            "OOP": 0.9,
            "Databases": 0.8
        },
        "user3": {
            "Programming Basics": 0.7,
            "Data Structures": 0.6,
            "Algorithms": 0.5,
            "OOP": 0.8,
            "Databases": 0.9
        }
    }

def test_recommender_initialization(sample_user_topic_matrix):
    recommender = CollaborativeFilteringRecommender(sample_user_topic_matrix)
    assert len(recommender.users) == 3
    assert len(recommender.topics) == 5
    assert recommender.matrix.shape == (3, 5)

def test_get_similar_users(sample_user_topic_matrix):
    recommender = CollaborativeFilteringRecommender(sample_user_topic_matrix)
    similar_users = recommender._get_similar_users("user1", n_neighbors=2)
    assert len(similar_users) == 2
    assert all(isinstance(similarity, float) for _, similarity in similar_users)

def test_recommend_for_user(sample_user_topic_matrix):
    recommender = CollaborativeFilteringRecommender(sample_user_topic_matrix)
    recommendations = recommender.recommend("user1", top_k=2)
    assert len(recommendations) <= 2
    assert all(isinstance(rec, str) for rec in recommendations)

def test_recommend_for_new_user(sample_user_topic_matrix):
    recommender = CollaborativeFilteringRecommender(sample_user_topic_matrix)
    recommendations = recommender.recommend("new_user")
    assert recommendations == []

def test_recommend_with_empty_matrix():
    recommender = CollaborativeFilteringRecommender({})
    recommendations = recommender.recommend("user1")
    assert recommendations == [] 
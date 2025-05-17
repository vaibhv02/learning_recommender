import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

class CollaborativeFilteringRecommender:
    def __init__(self, user_topic_matrix: Dict[str, Dict[str, float]]):
        """
        Initialize the recommender with a user-topic matrix.
        
        Args:
            user_topic_matrix: Dictionary mapping user_ids to their topic mastery scores
                              {user_id: {topic: mastery_score}}
        """
        self.user_topic_matrix = user_topic_matrix
        self.users = list(user_topic_matrix.keys())
        self.topics = list(set().union(*[set(scores.keys()) for scores in user_topic_matrix.values()]))
        self.topic_to_idx = {topic: idx for idx, topic in enumerate(self.topics)}
        self.user_to_idx = {user: idx for idx, user in enumerate(self.users)}
        
        # Convert to numpy array for faster computation
        self.matrix = np.zeros((len(self.users), len(self.topics)))
        for user, scores in user_topic_matrix.items():
            for topic, score in scores.items():
                self.matrix[self.user_to_idx[user], self.topic_to_idx[topic]] = score

    def _get_similar_users(self, user_id: str, n_neighbors: int = 5) -> List[Tuple[str, float]]:
        """Find similar users based on cosine similarity."""
        if user_id not in self.user_to_idx:
            return []
            
        user_idx = self.user_to_idx[user_id]
        user_vector = self.matrix[user_idx].reshape(1, -1)
        
        # Calculate cosine similarity with all users
        similarities = cosine_similarity(user_vector, self.matrix)[0]
        
        # Get top N similar users (excluding the user themselves)
        similar_indices = np.argsort(similarities)[::-1][1:n_neighbors+1]
        return [(self.users[idx], similarities[idx]) for idx in similar_indices]

    def recommend(self, user_id: str, top_k: int = 5) -> List[str]:
        """
        Recommend topics for a user based on similar users' preferences.
        
        Args:
            user_id: ID of the user to recommend for
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended topic names
        """
        if user_id not in self.user_to_idx:
            return []
            
        # Get similar users
        similar_users = self._get_similar_users(user_id)
        if not similar_users:
            return []
            
        # Get topics the user hasn't mastered yet
        user_scores = self.user_topic_matrix[user_id]
        unmastered_topics = [topic for topic in self.topics 
                           if topic not in user_scores or user_scores[topic] < 0.7]
        
        # Calculate weighted average mastery for each unmastered topic
        topic_scores = {}
        for topic in unmastered_topics:
            topic_idx = self.topic_to_idx[topic]
            weighted_sum = 0
            similarity_sum = 0
            
            for similar_user, similarity in similar_users:
                similar_user_idx = self.user_to_idx[similar_user]
                mastery = self.matrix[similar_user_idx, topic_idx]
                weighted_sum += mastery * similarity
                similarity_sum += similarity
                
            if similarity_sum > 0:
                topic_scores[topic] = weighted_sum / similarity_sum
        
        # Return top K topics
        return sorted(topic_scores.keys(), 
                     key=lambda x: topic_scores[x], 
                     reverse=True)[:top_k] 
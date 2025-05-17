def compute_mastery(quiz_score: float, time_spent: float, revisit_count: int) -> float:
    """
    Compute the mastery level of a topic based on various factors.
    
    Args:
        quiz_score (float): Score achieved in the quiz (0-100)
        time_spent (float): Time spent on the topic in minutes
        revisit_count (int): Number of times the topic was revisited
        
    Returns:
        float: Mastery level between 0 and 1
    """
    # Normalize quiz score to 0-1 range
    quiz_mastery = quiz_score / 100.0
    
    # Normalize time spent (assuming 60 minutes is optimal time)
    time_mastery = min(time_spent / 60.0, 1.0)
    
    # Normalize revisit count (assuming 3 revisits is optimal)
    revisit_mastery = min(revisit_count / 3.0, 1.0)
    
    # Weighted average of different factors
    # Quiz score is most important (50%), followed by time spent (30%) and revisits (20%)
    mastery = (
        0.5 * quiz_mastery +
        0.3 * time_mastery +
        0.2 * revisit_mastery
    )
    
    # Ensure mastery is between 0 and 1
    return max(0.0, min(1.0, mastery))

topic_map = {
    "Programming Basics": [],
    "Data Structures": ["Programming Basics"],
    "Algorithms": ["Data Structures"],
    "OOP": ["Programming Basics"],
    "Databases": ["Programming Basics"],
    "Operating Systems": ["Data Structures"],
}

def recommend_next_topics(user_mastery: dict, threshold: float = 0.7) -> list:
    """
    Recommend next topics for the user based on their mastery and topic prerequisites.
    Args:
        user_mastery (dict): {topic: mastery_score}
        threshold (float): Mastery threshold to consider a topic as mastered
    Returns:
        list: List of recommended topics to study next
    """
    recommendations = []
    for topic, prereqs in topic_map.items():
        if user_mastery.get(topic, 0) >= threshold:
            continue  # Already mastered
        if all(user_mastery.get(pr, 0) >= threshold for pr in prereqs):
            recommendations.append(topic)
    return recommendations

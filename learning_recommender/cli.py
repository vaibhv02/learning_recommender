from learning_recommender.recommender.rule_based import topic_map, recommend_next_topics

def main():
    print("Welcome to the Learning Recommender CLI!")
    user_mastery = {}
    print("\nEnter your mastery for each topic (0 to 1, or leave blank for 0):")
    for topic in topic_map:
        val = input(f"  {topic}: ")
        try:
            user_mastery[topic] = float(val) if val.strip() else 0.0
        except ValueError:
            user_mastery[topic] = 0.0
    recs = recommend_next_topics(user_mastery)
    print("\nRecommended next topics:")
    if recs:
        for t in recs:
            print(f"- {t}")
    else:
        print("You have mastered all topics! 🎉")

if __name__ == "__main__":
    main() 
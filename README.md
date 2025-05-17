## Learning Recommender System

**A BTech CSE Final Year Project**

### Project Overview

The Learning Recommender System is an AI-driven educational platform designed to provide personalized learning recommendations to B.Tech CSE students. It tailors recommendations based on individual learning patterns, mastery levels, and prerequisite relationships between topics.

![AI-driven Learning Recommender](https://img.freepik.com/free-vector/gradient-machine-learning-infographic_23-2149379690.jpg)

### Features

- **Rule-based Recommendations**: Suggests topics based on mastery levels and prerequisite relationships
- **Collaborative Filtering**: Uses patterns from similar users to recommend topics
- **Hybrid Approach**: Combines both methods for more accurate recommendations
- **Mastery Assessment**: Calculates mastery based on quiz scores, time spent, and revisits
- **Interactive Dashboard**: Visualizes learning progress and recommendations
- **Topic Explorer**: Explains relationships between different topics in the curriculum

### Tech Stack

- Python 3.9+
- Streamlit (UI Framework)
- NumPy and Pandas (Data Processing)
- Scikit-learn (Machine Learning Models)
- Pytest (Testing)

### Setup Instructions

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/learning_recommender.git
   cd learning_recommender
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Install the package in development mode**
   ```
   pip install -e .
   ```

5. **Run the tests to ensure everything is working**
   ```
   pytest
   ```

6. **Start the Streamlit application**
   ```
   streamlit run app.py
   ```

### Project Structure

- `learning_recommender/`: Main package
  - `recommender/`: Core recommendation algorithms
    - `rule_based.py`: Rule-based recommendation logic
    - `collaborative.py`: Collaborative filtering implementation
    - `dkt.py`: Deep Knowledge Tracing (future implementation)
    - `models.py`: Data models for users, topics, etc.
  - `cli.py`: Command line interface (for testing)
- `tests/`: Test suite
- `app.py`: Streamlit web application
- `requirements.txt`: Package dependencies
- `pyproject.toml`: Package configuration

### How to Present

1. **Start the application** before your presentation
2. **Explain the problem domain** - personalized education and adaptive learning
3. **Demonstrate the dashboard** showing existing users' mastery levels
4. **Show the recommendation system** in action
   - Rule-based recommendations
   - Collaborative filtering recommendations
   - Hybrid approach
5. **Demonstrate the Topic Assessment feature** to show how mastery is calculated
6. **Explain the architecture** and algorithms used
7. **Discuss future scope** and potential enhancements

### Future Scope

1. **Deep Knowledge Tracing**: Implementing more advanced mastery prediction
2. **Content-based Filtering**: Adding semantic understanding of topics
3. **Real-time Analytics**: Adding analytics dashboards for educators
4. **Integration with LMS**: Connecting with existing Learning Management Systems
5. **Mobile Application**: Developing a mobile interface for on-the-go learning

### 🎯 Success Metrics

| Metric Type | Metric              | Description                                                             | Initial Target |
|-------------|---------------------|-------------------------------------------------------------------------|----------------|
| **Offline** | Coverage            | % of users for whom the system can generate ≥1 valid recommendation     | ≥ 95%          |
|             | Rule-MVP Accuracy   | % match between rule-based suggestions and a gold-standard topic sequence | ≥ 60%          |
|             | CF Precision@5      | Precision of top-5 collaborative-filtering recommendations              | ≥ 0.30         |
|             | DKT AUC             | AUC of deep-knowledge-tracing model predicting mastery on next topic    | ≥ 0.70         |
| **Online**  | Engagement (CTR)    | Click-through rate on recommended topics                                | ≥ 20%          |
|             | Completion Rate     | % of recommended modules that learners finish                            | ≥ 70%          |
|             | Feedback Score      | Average self-reported usefulness rating (1–5 scale)                      | ≥ 4.0          |

## Chatbot Options

The Learning Recommender System offers two different chatbot implementations:

1. **Built-in Knowledge-Based Chatbot**: The original chatbot that uses a predefined knowledge base about CS topics, with web search capability for topics not in the knowledge base.

2. **Rasa-based Open Source Chatbot**: A more advanced chatbot using the Rasa open-source framework, which provides better conversational capabilities and can be extended with custom training data.

### Testing the Chatbot

To test the chatbot functionality, you can use the included CLI script:

```bash
python chatbot_cli.py
```

This will let you choose between the two chatbot implementations and interact with them in a conversational manner.

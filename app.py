import streamlit as st
import pandas as pd
import numpy as np
import time
import threading
import requests
from learning_recommender.recommender.rule_based import compute_mastery, recommend_next_topics, topic_map
from learning_recommender.recommender.collaborative import CollaborativeFilteringRecommender
from learning_recommender.recommender.models import User, Topic, UserProgress
from learning_recommender.recommender.deepseek_chatbot import DeepSeekChatbot

# App title and description
st.set_page_config(page_title="Learning Path Recommender System", layout="wide")

# Sample data - in a real app, this would come from a database
sample_users = {
    "user1": {"name": "Alice", "mastery": {
        "Programming Basics": 0.9,
        "Data Structures": 0.8, 
        "Algorithms": 0.7,
        "OOP": 0.6,
        "Databases": 0.5,
    }},
    "user2": {"name": "Bob", "mastery": {
        "Programming Basics": 0.8, 
        "Data Structures": 0.7,
        "Algorithms": 0.6, 
        "OOP": 0.9,
        "Databases": 0.8,
    }},
    "user3": {"name": "Charlie", "mastery": {
        "Programming Basics": 0.7,
        "Data Structures": 0.6,
        "Algorithms": 0.5, 
        "OOP": 0.8,
        "Databases": 0.9,
    }},
}

# Initialize collaborative filtering recommender
user_topic_matrix = {user_id: data["mastery"] for user_id, data in sample_users.items()}
cf_recommender = CollaborativeFilteringRecommender(user_topic_matrix)

# Add DeepSeek chatbot instance
ollama_url_default = "http://localhost:11434"
deepseek_model_default = "deepseek-r1:14b"

# Fetch available Ollama models for dropdown
ollama_models = []
try:
    resp = requests.get(f"{ollama_url_default}/api/tags")
    if resp.status_code == 200:
        data = resp.json()
        ollama_models = [m['name'] for m in data.get('models', [])]
except Exception:
    ollama_models = [deepseek_model_default]
if not ollama_models:
    ollama_models = [deepseek_model_default]

# Use session state to store DeepSeek settings and chatbot instance
if "deepseek_model_name" not in st.session_state:
    st.session_state.deepseek_model_name = deepseek_model_default
if "deepseek_ollama_url" not in st.session_state:
    st.session_state.deepseek_ollama_url = ollama_url_default
if "deepseek_chatbot" not in st.session_state:
    st.session_state.deepseek_chatbot = None
if "deepseek_last_settings" not in st.session_state:
    st.session_state.deepseek_last_settings = (deepseek_model_default, ollama_url_default)

# Store chat histories for each engine (now only deepseek)
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {
        "deepseek": []
    }
if "active_chatbot" not in st.session_state:
    st.session_state.active_chatbot = "deepseek"
if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.chat_histories[st.session_state.active_chatbot]

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Topic Assessment", "Topic Explorer", "Recommendations", "AI Chatbot", "About"])

if page == "Dashboard":
    st.title("Learning Path Recommender System")
    st.markdown("""
    This system provides personalized learning recommendations for B.Tech CSE fundamentals.
    It uses both rule-based and collaborative filtering techniques to suggest the most relevant topics.
    """)
    st.header("Dashboard")
    
    # User selection
    user_id = st.selectbox("Select User", list(sample_users.keys()))
    user_data = sample_users[user_id]
    
    # Display user mastery
    st.subheader(f"Mastery Levels for {user_data['name']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create mastery dataframe for visualization
        mastery_df = pd.DataFrame([
            {"Topic": topic, "Mastery": mastery} 
            for topic, mastery in user_data["mastery"].items()
        ])
        
        # Display mastery as a bar chart
        st.bar_chart(mastery_df.set_index("Topic"))
    
    with col2:
        # Display mastery as a table
        st.dataframe(
            mastery_df,
            column_config={
                "Mastery": st.column_config.ProgressColumn(
                    "Mastery Level",
                    help="Mastery level from 0 to 1",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                )
            },
            hide_index=True,
        )
    
    # Get recommendations
    rule_recs = recommend_next_topics(user_data["mastery"])
    cf_recs = cf_recommender.recommend(user_id, top_k=3)
    
    # Display recommendations
    st.subheader("Recommended Next Topics")
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.write("Rule-based Recommendations:")
        if rule_recs:
            for topic in rule_recs:
                st.info(f"📚 {topic}")
        else:
            st.success("You've mastered all topics! 🎓")
    
    with rec_col2:
        st.write("Collaborative Filtering Recommendations:")
        if cf_recs:
            for topic in cf_recs:
                st.info(f"📚 {topic}")
        else:
            st.warning("Not enough data for personalized recommendations.")

elif page == "Topic Assessment":
    st.header("Topic Assessment")
    st.subheader("Assess your knowledge on a specific topic")
    
    selected_topic = st.selectbox("Select Topic", list(topic_map.keys()))
    
    # Quiz score
    quiz_score = st.slider("Quiz Score (0-100)", 0, 100, 75)
    
    # Time spent
    time_spent = st.slider("Time Spent (minutes)", 0, 120, 30)
    
    # Revisit count
    revisit_count = st.slider("Number of Revisits", 0, 10, 2)
    
    # Calculate mastery
    if st.button("Calculate Mastery"):
        mastery = compute_mastery(quiz_score, time_spent, revisit_count)
        
        # Display result
        st.subheader(f"Your Mastery of {selected_topic}")
        st.progress(mastery)
        st.metric("Mastery Score", f"{mastery:.2f}")
        
        # Interpretation
        if mastery >= 0.8:
            st.success("Excellent! You have mastered this topic. 🌟")
        elif mastery >= 0.6:
            st.info("Good understanding. Keep practicing to master it fully. 👍")
        elif mastery >= 0.4:
            st.warning("You're making progress. More practice needed. 📈")
        else:
            st.error("You need more work on this topic. Consider revisiting the basics. 📚")

elif page == "Topic Explorer":
    st.header("Topic Explorer")
    
    # Display topic prerequisites
    st.subheader("Topic Prerequisites Map")
    
    # Create a dataframe for the topic map
    topic_df = pd.DataFrame([
        {"Topic": topic, "Prerequisites": ", ".join(prereqs) if prereqs else "None"} 
        for topic, prereqs in topic_map.items()
    ])
    
    st.dataframe(topic_df, hide_index=True)
    
    # Visualization of topic dependencies
    st.subheader("Topic Dependencies")
    
    # Create data for the graph (simplified visualization)
    topics = list(topic_map.keys())
    edges = []
    
    for topic, prereqs in topic_map.items():
        for prereq in prereqs:
            edges.append((prereq, topic))
    
    # Display as a simple text-based graph
    for topic in topics:
        st.write(f"**{topic}** depends on:")
        dependencies = [edge[0] for edge in edges if edge[1] == topic]
        if dependencies:
            for dep in dependencies:
                st.write(f"  • {dep}")
        else:
            st.write("  • No prerequisites")
        st.write("---")

elif page == "Recommendations":
    st.title("Learning Path Recommender System")
    st.markdown("""
    This system provides personalized learning recommendations for B.Tech CSE fundamentals.
    It uses both rule-based and collaborative filtering techniques to suggest the most relevant topics.
    """)
    st.header("Recommendations")
    
    # Option to create a new user or select existing
    user_option = st.radio("User Selection", ["Select Existing User", "Create New User"])
    
    if user_option == "Select Existing User":
        user_id = st.selectbox("Select User", list(sample_users.keys()))
        user_data = sample_users[user_id]
        mastery_data = user_data["mastery"]
    else:
        st.subheader("Enter your mastery levels")
        
        mastery_data = {}
        for topic in topic_map.keys():
            mastery_data[topic] = st.slider(
                f"Mastery of {topic}", 0.0, 1.0, 0.5, 0.1
            )
    
    # Select recommendation method
    rec_method = st.radio(
        "Recommendation Method", 
        ["Rule-based", "Collaborative Filtering", "Hybrid"]
    )
    
    if st.button("Get Recommendations"):
        if rec_method == "Rule-based":
            recommendations = recommend_next_topics(mastery_data)
            rec_source = "Rule-based"
        elif rec_method == "Collaborative Filtering":
            if user_option == "Select Existing User":
                recommendations = cf_recommender.recommend(user_id, top_k=5)
            else:
                # For new users, we'd need to add them to the matrix
                # For demo purposes, just use rule-based
                recommendations = recommend_next_topics(mastery_data)
                st.info("For new users, collaborative filtering uses rule-based fallback.")
            rec_source = "Collaborative Filtering"
        else:  # Hybrid
            rule_recs = set(recommend_next_topics(mastery_data))
            if user_option == "Select Existing User":
                cf_recs = set(cf_recommender.recommend(user_id, top_k=5))
            else:
                cf_recs = set()
            
            # Hybrid approach: prioritize topics in both lists, then add others
            recommendations = list(rule_recs.intersection(cf_recs)) + list(rule_recs.difference(cf_recs)) + list(cf_recs.difference(rule_recs))
            recommendations = recommendations[:5]  # Limit to top 5
            rec_source = "Hybrid"
        
        # Display recommendations
        st.subheader(f"Recommended Topics ({rec_source})")
        if recommendations:
            for i, topic in enumerate(recommendations, 1):
                st.success(f"{i}. {topic}")
                
                # Show topic details
                if topic in topic_map:
                    prereqs = topic_map[topic]
                    if prereqs:
                        st.info(f"Prerequisites: {', '.join(prereqs)}")
        else:
            st.warning("No recommendations available. You may have mastered all topics!")

elif page == "AI Chatbot":
    st.title("AI Chatbot Assistant")
    st.markdown("""
    Ask any question about computer science topics, and get answers powered by a local large language model (DeepSeek via Ollama).
    """)
    st.subheader("Ask questions about any CS topic")
    
    # Only show DeepSeek Ollama Settings and use DeepSeekChatbot
    with st.expander("DeepSeek Ollama Settings", expanded=False):
        model_name = st.selectbox(
            "Ollama Model Name",
            ollama_models,
            index=ollama_models.index(st.session_state.deepseek_model_name) if st.session_state.deepseek_model_name in ollama_models else 0,
            key="deepseek_model_name_input"
        )
        ollama_url = st.text_input("Ollama Server URL", value=st.session_state.deepseek_ollama_url, key="deepseek_ollama_url_input")
        if model_name != st.session_state.deepseek_model_name:
            st.session_state.deepseek_model_name = model_name
        if ollama_url != st.session_state.deepseek_ollama_url:
            st.session_state.deepseek_ollama_url = ollama_url
    if (st.session_state.deepseek_model_name, st.session_state.deepseek_ollama_url) != st.session_state.deepseek_last_settings or st.session_state.deepseek_chatbot is None:
        st.session_state.deepseek_chatbot = DeepSeekChatbot(st.session_state.deepseek_ollama_url, st.session_state.deepseek_model_name)
        st.session_state.deepseek_last_settings = (st.session_state.deepseek_model_name, st.session_state.deepseek_ollama_url)
    chatbot = st.session_state.deepseek_chatbot
    selected_engine = "deepseek"
    
    # Remove About this AI Assistant logic for original chatbot, only show DeepSeek info
    with st.expander("About this AI Assistant"):
        st.markdown("""
        This AI assistant uses the DeepSeek LLM running locally via Ollama.
        
        **Features:**
        - State-of-the-art large language model (DeepSeek)
        - No internet required (runs locally via Ollama)
        - Can answer a wide range of questions, not limited to a fixed knowledge base
        - Remembers your conversation history (in this session)
        """)
        st.markdown("""
        **Try asking questions like:**
        - "What is Machine Learning?"
        - "What are the main concepts in Cybersecurity?"
        - "Give me examples of Cloud Computing applications"
        - "What topics are related to Artificial Intelligence?"
        """)
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about CS topics!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            response_text = ""
            for chunk in chatbot.stream_response(prompt):
                response_text += chunk
                thinking_placeholder.markdown(response_text + "▌")
            thinking_placeholder.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

elif page == "About":
    st.header("About the Learning Recommender System")
    
    st.markdown("""
    ## Project Overview
    This Learning Recommender System is a BTech CSE final year project that provides personalized 
    learning recommendations for computer science students.
    
    ## Features
    - **Rule-based Recommendations**: Uses topic prerequisites and mastery levels to suggest topics
    - **Collaborative Filtering**: Recommends topics based on similar users' learning patterns
    - **Hybrid Approach**: Combines both methods for more accurate recommendations
    - **Mastery Assessment**: Calculates mastery based on quiz scores, time spent, and revisits
    
    ## Technologies Used
    - Python
    - Streamlit
    - NumPy
    - Pandas
    - Scikit-learn
    
    ## Future Scope
    - Integration with real learning management systems
    - Deep Knowledge Tracing for more accurate mastery prediction
    - Content-based recommendations using topic similarity
    - Mobile application for on-the-go learning
    - Integration with online learning platforms
    """)

    # Update AI Techniques section
    st.markdown("""
    ## AI Techniques Used
    
    This system incorporates several AI and machine learning techniques:
    
    - **Collaborative Filtering**: Uses cosine similarity to identify users with similar learning patterns and make recommendations based on their experiences.
    
    - **Hybrid Recommendation Engine**: Combines rule-based and collaborative filtering approaches to provide more accurate and diverse recommendations.
    
    - **Natural Language Processing**: Powers the AI chatbot to understand topic-related questions and provide relevant information from the knowledge base.
    
    - **Web Search Integration**: The chatbot can search the web for information that isn't in its knowledge base, extending its capabilities significantly.
    
    - **Rule-based Expert System**: Computes mastery levels based on multiple parameters with weighted importance.
    
    ## Future AI Enhancements
    
    - **Deep Knowledge Tracing**: Neural network models to predict knowledge state transitions over time.
    
    - **Content-based Recommendations**: Analyzing the actual content of learning materials to find semantic connections.
    
    - **Reinforcement Learning**: Optimizing recommendation strategies based on learning outcomes.
    
    - **Advanced NLP with BERT/GPT**: Enhancing the chatbot with state-of-the-art language models for better understanding and responses.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("BTech CSE Final Year Project") 
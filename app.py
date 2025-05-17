import streamlit as st
import pandas as pd
import numpy as np
import time
import threading
from learning_recommender.recommender.rule_based import compute_mastery, recommend_next_topics, topic_map
from learning_recommender.recommender.collaborative import CollaborativeFilteringRecommender
from learning_recommender.recommender.models import User, Topic, UserProgress
from learning_recommender.recommender.chatbot import TopicChatbot, get_extended_knowledge_base
from learning_recommender.recommender.rasa_chatbot import RasaChatbot, create_rasa_chatbot

# App title and description
st.set_page_config(page_title="Learning Path Recommender System", layout="wide")
st.title("Learning Path Recommender System")
st.markdown("""
This system provides personalized learning recommendations for B.Tech CSE fundamentals.
It uses both rule-based and collaborative filtering techniques to suggest the most relevant topics.
""")

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

# Initialize the chatbot with extended knowledge base and web search capability
original_chatbot = TopicChatbot(get_extended_knowledge_base(), use_web_search=True)
rasa_chatbot = None  # Will be initialized only when needed
active_chatbot = "original"  # Keep track of which chatbot is active

# Initialize rasa server process
rasa_server_thread = None

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Topic Assessment", "Topic Explorer", "Recommendations", "AI Chatbot", "About"])

if page == "Dashboard":
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
    st.header("AI Learning Assistant")
    st.subheader("Ask questions about any CS topic")
    
    # Chatbot selection
    chatbot_option = st.radio(
        "Select Chatbot Engine",
        ["Original Knowledge-Based Chatbot", "Rasa Open Source Chatbot"]
    )
    
    # Web search toggle
    use_web_search = st.toggle("Enable Web Search for Unknown Topics", value=True)
    
    # Initialize the selected chatbot if needed
    if chatbot_option == "Original Knowledge-Based Chatbot":
        chatbot = original_chatbot
        chatbot.use_web_search = use_web_search
        
        if active_chatbot != "original":
            # Reset chat if switching chatbot types
            if "messages" in st.session_state:
                st.session_state.messages = []
            active_chatbot = "original"
            
    else:  # Rasa chatbot selected
        if rasa_chatbot is None:
            # Show initialization message
            init_placeholder = st.empty()
            init_placeholder.info("Initializing Rasa chatbot. This may take a minute...")
            
            # Initialize and start Rasa server
            rasa_chatbot = create_rasa_chatbot(use_web_search=use_web_search)
            
            # Start the server in a separate thread to prevent blocking the UI
            def start_rasa_server():
                success = rasa_chatbot.start_server()
                if not success:
                    st.error("Failed to start Rasa server. Using original chatbot as fallback.")
                    return False
                return True
            
            rasa_server_thread = threading.Thread(target=start_rasa_server)
            rasa_server_thread.daemon = True
            rasa_server_thread.start()
            
            # Wait for server to start
            time.sleep(5)
            init_placeholder.empty()
        
        chatbot = rasa_chatbot
        chatbot.use_web_search = use_web_search
        
        if active_chatbot != "rasa":
            # Reset chat if switching chatbot types
            if "messages" in st.session_state:
                st.session_state.messages = []
            active_chatbot = "rasa"
    
    # Information about the chatbot
    with st.expander("About this AI Assistant"):
        if chatbot_option == "Original Knowledge-Based Chatbot":
            st.markdown("""
            This AI assistant uses a curated knowledge base to answer questions about Computer Science topics.
            
            **Features:**
            - Answers questions about definitions, concepts, examples, and related topics
            - Can search the web for topics not in its knowledge base (when enabled)
            - Remembers your conversation history
            
            **Available Topics:**
            The assistant has detailed knowledge about core CS topics like Programming, Data Structures, 
            Algorithms, OOP, Databases, Operating Systems, and advanced topics like Artificial Intelligence, 
            Machine Learning, Web Development, Cybersecurity, Computer Networks and more.
            """)
        else:
            st.markdown("""
            This AI assistant uses the Rasa open-source framework to power conversational interactions.
            
            **Features:**
            - More natural conversational flow with context tracking
            - Intent recognition and entity extraction
            - Can fall back to web search for unknown topics
            - Open-source architecture that can be extended and customized
            
            **Specialized Topics:**
            The Rasa assistant is trained specifically on data structures, algorithms, programming basics,
            and web development, with the ability to learn more topics over time.
            """)
            
        st.markdown("""
        **Try asking questions like:**
        - "What is Machine Learning?"
        - "What are the main concepts in Cybersecurity?"
        - "Give me examples of Cloud Computing applications"
        - "What topics are related to Artificial Intelligence?"
        """)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about CS topics!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show thinking indicator
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("Thinking...")
            
            # Generate and display assistant response
            response = chatbot.generate_response(prompt)
            thinking_placeholder.empty()
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with topic suggestions
    with st.sidebar:
        st.markdown("### Topic Suggestions")
        st.markdown("Try asking about:")
        
        if chatbot_option == "Original Knowledge-Based Chatbot":
            # Display topics from our extended knowledge base
            for topic in get_extended_knowledge_base().keys():
                with st.expander(topic):
                    st.markdown(f"- What is {topic}?")
                    st.markdown(f"- What are the main concepts in {topic}?")
                    st.markdown(f"- Give me examples of {topic}")
                    st.markdown(f"- What topics are related to {topic}?")
        else:
            # For Rasa, show the specialized topics it's trained on
            specialized_topics = ["Data Structures", "Algorithms", "Programming Basics", "Web Development"]
            for topic in specialized_topics:
                with st.expander(topic):
                    st.markdown(f"- What is {topic}?")
                    st.markdown(f"- Explain {topic}")
                    st.markdown(f"- Tell me about {topic}")

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

# Clean up Rasa server when the app stops
def cleanup():
    if rasa_chatbot is not None:
        rasa_chatbot.stop_server()

# Register cleanup to happen at exit
import atexit
atexit.register(cleanup)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("BTech CSE Final Year Project") 
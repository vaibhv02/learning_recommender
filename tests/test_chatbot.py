import pytest
from learning_recommender.recommender.chatbot import TopicChatbot, get_sample_knowledge_base, get_extended_knowledge_base

@pytest.fixture
def simple_chatbot():
    return TopicChatbot(get_sample_knowledge_base(), use_web_search=False)

@pytest.fixture
def extended_chatbot():
    return TopicChatbot(get_extended_knowledge_base(), use_web_search=False)

@pytest.fixture
def web_chatbot():
    return TopicChatbot(get_sample_knowledge_base(), use_web_search=True)

def test_chatbot_greeting(simple_chatbot):
    response = simple_chatbot.generate_response("Hello")
    assert "Hello" in response or "Hi" in response or "Welcome" in response

def test_chatbot_topic_definition(simple_chatbot):
    response = simple_chatbot.generate_response("What is Data Structures?")
    assert "Data Structures" in response
    assert "organize" in response or "store" in response

def test_chatbot_topic_concepts(simple_chatbot):
    response = simple_chatbot.generate_response("What are the main concepts in Algorithms?")
    assert "Algorithms" in response
    assert "sorting" in response.lower() or "searching" in response.lower()

def test_chatbot_topic_examples(simple_chatbot):
    response = simple_chatbot.generate_response("Can you give me some examples of OOP?")
    assert "OOP" in response
    assert "class" in response.lower() or "banking" in response.lower()

def test_chatbot_topic_related(simple_chatbot):
    response = simple_chatbot.generate_response("What topics are related to Databases?")
    assert "Databases" in response
    assert "Data Structures" in response or "Operating Systems" in response

def test_chatbot_unknown_topic(simple_chatbot):
    response = simple_chatbot.generate_response("Tell me about Quantum Computing")
    assert "don't have" in response.lower() or "not familiar" in response.lower()
    # Should suggest known topics
    known_topics = get_sample_knowledge_base().keys()
    assert any(topic in response for topic in known_topics)

def test_extended_chatbot_has_more_topics(simple_chatbot, extended_chatbot):
    # Test that extended chatbot has more topics than the simple one
    assert len(extended_chatbot.topics) > len(simple_chatbot.topics)
    assert "Artificial Intelligence" in extended_chatbot.topics
    assert "Machine Learning" in extended_chatbot.topics
    
def test_extended_chatbot_answers_ai_questions(extended_chatbot):
    response = extended_chatbot.generate_response("What is Artificial Intelligence?")
    assert "Artificial Intelligence" in response
    assert "intelligence" in response.lower() or "human" in response.lower()

def test_web_search_unknown_topic(web_chatbot, monkeypatch):
    # Mock the web search function to return predictable results for testing
    def mock_search(*args, **kwargs):
        return "Quantum computing uses quantum mechanics principles to process information."
    
    # Apply the mock
    monkeypatch.setattr(web_chatbot, "_search_web", mock_search)
    
    # Test with a topic not in our knowledge base
    response = web_chatbot.generate_response("What is Quantum Computing?")
    assert "Quantum computing" in response or "quantum mechanics" in response.lower()
    
def test_web_search_disabled_for_unknown_topic(web_chatbot):
    # Disable web search
    web_chatbot.use_web_search = False
    
    # Test with a topic not in our knowledge base
    response = web_chatbot.generate_response("What is Quantum Computing?")
    assert "don't have" in response.lower() or "not familiar" in response.lower()
    
    # Re-enable web search for other tests
    web_chatbot.use_web_search = True 
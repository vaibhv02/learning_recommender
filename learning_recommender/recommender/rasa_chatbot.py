"""
This module implements a chatbot for the Learning Recommender system using Rasa.
Rasa is an open-source chatbot framework that uses machine learning to understand
and respond to user messages.
"""

import os
import subprocess
import json
import requests
from typing import Dict, List, Optional, Any, Tuple

class RasaChatbot:
    def __init__(self, 
                 model_directory: str = "models",
                 rasa_server_url: str = "http://localhost:5005",
                 use_web_search: bool = True):
        """
        Initialize the Rasa chatbot for CS education.
        
        Args:
            model_directory: Directory where Rasa models are stored
            rasa_server_url: URL of the Rasa server
            use_web_search: Whether to use web search for unanswered questions
        """
        self.model_directory = model_directory
        self.rasa_server_url = rasa_server_url
        self.use_web_search = use_web_search
        self.server_process = None
        
        # Create Rasa project structure if it doesn't exist
        self._setup_rasa_project()
    
    def _setup_rasa_project(self):
        """Setup the initial Rasa project structure if it doesn't exist."""
        # Check if model directory exists
        if not os.path.exists(self.model_directory):
            os.makedirs(self.model_directory, exist_ok=True)
        
        # Create Rasa project directory
        rasa_dir = "rasa_chatbot"
        if not os.path.exists(rasa_dir):
            os.makedirs(rasa_dir, exist_ok=True)
            
            # Initialize Rasa project
            try:
                subprocess.run(["rasa", "init", "--no-prompt"], 
                               cwd=rasa_dir, 
                               check=True)
                
                # Customize training data for CS topics
                self._create_cs_training_data(rasa_dir)
            except Exception as e:
                print(f"Error initializing Rasa project: {e}")
    
    def _create_cs_training_data(self, rasa_dir: str):
        """
        Create custom training data for CS topics.
        
        Args:
            rasa_dir: Path to the Rasa project directory
        """
        # Define CS-specific intents and responses
        cs_nlu_data = {
            "version": "3.1",
            "nlu": [
                {
                    "intent": "ask_data_structures",
                    "examples": [
                        "What are data structures?",
                        "Explain linked lists",
                        "Tell me about arrays",
                        "How do hash tables work?",
                        "What is a tree in data structures?",
                        "Explain stacks and queues"
                    ]
                },
                {
                    "intent": "ask_algorithms",
                    "examples": [
                        "What are algorithms?",
                        "Explain sorting algorithms",
                        "Tell me about search algorithms",
                        "How does quicksort work?",
                        "What is dynamic programming?",
                        "Explain big O notation"
                    ]
                },
                {
                    "intent": "ask_programming_basics",
                    "examples": [
                        "What are variables?",
                        "Explain loops in programming",
                        "Tell me about conditionals",
                        "How do functions work?",
                        "What are data types?",
                        "Explain object-oriented programming"
                    ]
                },
                {
                    "intent": "ask_web_development",
                    "examples": [
                        "What is HTML?",
                        "Explain CSS",
                        "Tell me about JavaScript",
                        "How do web servers work?",
                        "What is responsive design?",
                        "Explain APIs"
                    ]
                }
            ]
        }
        
        # Write custom NLU data
        nlu_file = os.path.join(rasa_dir, "data", "nlu.yml")
        with open(nlu_file, 'w') as f:
            f.write("version: \"3.1\"\n\nnlu:\n")
            for intent in cs_nlu_data["nlu"]:
                f.write(f"- intent: {intent['intent']}\n  examples: |\n")
                for example in intent["examples"]:
                    f.write(f"    - {example}\n")
        
        # Create domain with CS-specific responses
        domain_data = {
            "version": "3.1",
            "intents": [
                "ask_data_structures",
                "ask_algorithms",
                "ask_programming_basics",
                "ask_web_development",
                "greet",
                "goodbye",
                "affirm",
                "deny",
                "mood_great",
                "mood_unhappy",
                "bot_challenge"
            ],
            "responses": {
                "utter_data_structures": [
                    {"text": "Data structures are specialized formats for organizing and storing data. Common data structures include arrays, linked lists, stacks, queues, trees, and hash tables. Each has different characteristics in terms of time complexity for operations like access, search, insert, and delete."}
                ],
                "utter_algorithms": [
                    {"text": "Algorithms are step-by-step procedures for solving problems. They're fundamental to computer science and programming. Examples include sorting algorithms (like quicksort, mergesort), search algorithms (binary search), and graph algorithms (Dijkstra's, BFS, DFS)."}
                ],
                "utter_programming_basics": [
                    {"text": "Programming basics include concepts like variables, data types, control structures (if/else, loops), functions, and objects. These are the building blocks that allow you to create programs to solve problems and automate tasks."}
                ],
                "utter_web_development": [
                    {"text": "Web development involves creating websites and web applications. Frontend development uses HTML (structure), CSS (styling), and JavaScript (interactivity). Backend development involves server-side programming, databases, and APIs to handle data and business logic."}
                ]
            }
        }
        
        # Add default responses
        default_responses = {
            "utter_greet": [{"text": "Hey! How can I help you with computer science today?"}],
            "utter_cheer_up": [{"text": "Don't worry! Computer science can be challenging, but you'll get it with practice."}],
            "utter_did_that_help": [{"text": "Did that help you understand the concept better?"}],
            "utter_happy": [{"text": "Great! What else would you like to learn about?"}],
            "utter_goodbye": [{"text": "Bye! Keep coding and learning!"}],
            "utter_iamabot": [{"text": "I am a chatbot designed to help you learn computer science concepts."}]
        }
        domain_data["responses"].update(default_responses)
        
        # Write domain file
        domain_file = os.path.join(rasa_dir, "domain.yml")
        with open(domain_file, 'w') as f:
            f.write("version: \"3.1\"\n\n")
            
            # Write intents
            f.write("intents:\n")
            for intent in domain_data["intents"]:
                f.write(f"  - {intent}\n")
            
            f.write("\nresponses:\n")
            for response_key, response_list in domain_data["responses"].items():
                f.write(f"  {response_key}:\n")
                for response in response_list:
                    f.write(f"  - text: \"{response['text']}\"\n")

        # Create custom stories
        stories_data = """version: "3.1"

stories:
- story: data structures path
  steps:
  - intent: greet
  - action: utter_greet
  - intent: ask_data_structures
  - action: utter_data_structures
  - intent: goodbye
  - action: utter_goodbye

- story: algorithms path
  steps:
  - intent: greet
  - action: utter_greet
  - intent: ask_algorithms
  - action: utter_algorithms
  - intent: goodbye
  - action: utter_goodbye

- story: programming basics path
  steps:
  - intent: ask_programming_basics
  - action: utter_programming_basics

- story: web development path
  steps:
  - intent: ask_web_development
  - action: utter_web_development
"""
        
        # Write stories file
        stories_file = os.path.join(rasa_dir, "data", "stories.yml")
        with open(stories_file, 'w') as f:
            f.write(stories_data)
    
    def start_server(self):
        """Start the Rasa server in the background."""
        try:
            # Train the model first
            subprocess.run(["rasa", "train"], 
                          cwd="rasa_chatbot", 
                          check=True)
            
            # Start the server
            self.server_process = subprocess.Popen(
                ["rasa", "run", "--enable-api", "--cors", "*"],
                cwd="rasa_chatbot"
            )
            print("Rasa server started successfully")
            return True
        except Exception as e:
            print(f"Failed to start Rasa server: {e}")
            return False
    
    def stop_server(self):
        """Stop the Rasa server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            print("Rasa server stopped")
    
    def generate_response(self, question: str) -> str:
        """
        Generate a response to a user question using Rasa.
        
        Args:
            question: The user's question
            
        Returns:
            Chatbot response
        """
        try:
            # Send the message to the Rasa server
            response = requests.post(
                f"{self.rasa_server_url}/webhooks/rest/webhook",
                json={"sender": "user", "message": question}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and "text" in result[0]:
                    return result[0]["text"]
            
            # Fallback to web search if enabled and no response from Rasa
            if self.use_web_search:
                from .chatbot import TopicChatbot
                fallback_chatbot = TopicChatbot({}, use_web_search=True)
                return fallback_chatbot._search_web(question)
            
            return "I'm sorry, I don't have information about that topic yet."
            
        except Exception as e:
            print(f"Error communicating with Rasa server: {e}")
            return f"Sorry, there was an error processing your question. Please try again later."

    def __del__(self):
        """Clean up resources when the object is deleted."""
        self.stop_server()


# Helper function to create a Rasa chatbot instance
def create_rasa_chatbot(use_web_search: bool = True) -> RasaChatbot:
    """
    Create and return a Rasa chatbot instance.
    
    Args:
        use_web_search: Whether to enable web search for fallback
        
    Returns:
        A configured RasaChatbot instance
    """
    chatbot = RasaChatbot(use_web_search=use_web_search)
    return chatbot 
"""
Demo script for chatbot integration in the Learning Recommender System.
This script demonstrates how to use both the original chatbot and the Rasa-based chatbot.
"""

import os
import sys
import time

# Import the chatbot modules
from .chatbot import TopicChatbot, get_extended_knowledge_base
from .rasa_chatbot import RasaChatbot, create_rasa_chatbot
from .deepseek_chatbot import DeepSeekChatbot

def run_demo():
    """Run a demo of the chatbot integration."""
    print("==== Learning Recommender System - Chatbot Demo ====")
    print("\nThis demo shows how to use three different chatbot backends:")
    print("1. Original Rule-based Chatbot")
    print("2. Rasa-based Chatbot (Open Source)")
    print("3. DeepSeek LLM Chatbot (Offline)")
    
    choice = input("\nChoose a chatbot to test (1, 2, or 3): ")
    
    if choice == "1":
        print("\n=== Testing Original Chatbot ===")
        # Initialize the original chatbot with the knowledge base
        kb = get_extended_knowledge_base()
        chatbot = TopicChatbot(kb, use_web_search=True)
        chatbot_type = "Original"
    elif choice == "2":
        print("\n=== Testing Rasa Chatbot ===")
        print("Initializing Rasa chatbot... (this may take a minute)")
        # Initialize and start the Rasa server
        chatbot = create_rasa_chatbot(use_web_search=True)
        success = chatbot.start_server()
        if not success:
            print("Failed to start Rasa server. Falling back to original chatbot.")
            kb = get_extended_knowledge_base()
            chatbot = TopicChatbot(kb, use_web_search=True)
            chatbot_type = "Original (fallback)"
        else:
            print("Waiting for Rasa server to start...")
            time.sleep(5)  # Give the server time to start
            chatbot_type = "Rasa"
    elif choice == "3":
        print("\n=== Testing DeepSeek Chatbot (Ollama) ===")
        model_name = input("Enter the Ollama model name (default: deepseek-r1:14b): ").strip() or "deepseek-r1:14b"
        ollama_url = input("Enter the Ollama server URL (default: http://localhost:11434): ").strip() or "http://localhost:11434"
        chatbot = DeepSeekChatbot(ollama_url, model_name)
        chatbot_type = "DeepSeek"
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Interactive chatbot loop
    print(f"\n=== {chatbot_type} Chatbot Ready ===")
    print("Type 'exit' or 'quit' to end the conversation.")
    
    while True:
        question = input("\nYou: ")
        if question.lower() in ["exit", "quit", "bye"]:
            break
        
        # Generate a response
        response = chatbot.generate_response(question)
        print(f"\nChatbot: {response}")
    
    # Clean up resources
    if chatbot_type == "Rasa":
        print("Stopping Rasa server...")
        chatbot.stop_server()
    
    print("\nThank you for trying the Learning Recommender System Chatbot!")

if __name__ == "__main__":
    run_demo() 
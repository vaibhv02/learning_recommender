#!/usr/bin/env python3
"""
Command-line interface for the Learning Recommender System chatbot.
Run this script to test the different chatbot backends.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the demo script
from learning_recommender.recommender.chatbot_demo import run_demo

if __name__ == "__main__":
    run_demo() 
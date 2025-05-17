#!/bin/bash
# Run the Streamlit app for the Learning Recommender System

echo "Starting Learning Recommender System Streamlit app..."
echo "Ensure you've installed the requirements with: pip install -r requirements.txt"
echo

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit is not installed. Installing now..."
    pip install streamlit
fi

# Run Streamlit app
streamlit run app.py

echo "Streamlit app has stopped. Cleaning up..." 
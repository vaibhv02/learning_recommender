from typing import Dict, List, Tuple
import re
import requests
import json
import os
import random
from time import sleep

class TopicChatbot:
    def __init__(self, topic_knowledge_base: Dict[str, Dict[str, str]], use_web_search: bool = False):
        """
        Initialize the chatbot with a knowledge base about topics.
        
        Args:
            topic_knowledge_base: Dictionary mapping topics to info
                Format: {topic: {"definition": "...", "concepts": "...", "examples": "..."}}
            use_web_search: Whether to use web search when local knowledge is insufficient
        """
        self.knowledge_base = topic_knowledge_base
        self.topics = list(topic_knowledge_base.keys())
        self.use_web_search = use_web_search
        
        # Pre-defined response templates
        self.templates = {
            "definition": [
                "Here's what I know about {topic}: {content}",
                "{topic} refers to: {content}",
                "In computer science, {topic} is defined as: {content}"
            ],
            "concepts": [
                "Key concepts in {topic} include: {content}",
                "When studying {topic}, focus on: {content}",
                "The main ideas in {topic} are: {content}"
            ],
            "examples": [
                "Here are some examples of {topic}: {content}",
                "To understand {topic}, consider these examples: {content}",
                "Practical applications of {topic} include: {content}"
            ],
            "related": [
                "Topics related to {topic} include: {content}",
                "After learning {topic}, you might want to explore: {content}",
                "If you're interested in {topic}, also check out: {content}"
            ],
            "not_found": [
                "I don't have specific information about that. Can you try asking about one of these topics? {topics}",
                "I'm not familiar with that specific query. I can answer questions about: {topics}",
                "I don't have details on that. Try asking about: {topics}"
            ],
            "greeting": [
                "Hello! I'm your CS Learning Assistant. How can I help you today?",
                "Hi there! I can answer questions about CS topics. What would you like to know?",
                "Welcome! I'm here to help with your computer science learning. Ask me anything about our topics!"
            ],
            "thanks": [
                "You're welcome! Let me know if you have more questions.",
                "Happy to help! Feel free to ask more questions about any topic.",
                "No problem! I'm here to support your learning journey."
            ],
            "web_search": [
                "I found this information online: {content}",
                "Based on web search results: {content}",
                "According to online resources: {content}"
            ]
        }
    
    def _identify_topic_and_intent(self, question: str) -> Tuple[str, str]:
        """
        Identify the topic and intent from the user's question.
        
        Args:
            question: The user's question
            
        Returns:
            Tuple of (topic, intent)
        """
        # Convert to lowercase for easier matching
        question = question.lower()
        
        # Common typos and alternative terms
        question = question.replace("link list", "linked list")
        
        # Common CS concepts that might not be full topics but should be recognized
        cs_concepts = {
            "array": "Data Structures",
            "list": "Data Structures",
            "linked list": "Data Structures",
            "stack": "Data Structures",
            "queue": "Data Structures",
            "tree": "Data Structures",
            "graph": "Data Structures",
            "hash table": "Data Structures",
            "hash map": "Data Structures",
            "linked list": "Data Structures",
            "heap": "Data Structures",
            "sorting": "Algorithms",
            "searching": "Algorithms",
            "recursion": "Algorithms",
            "dynamic programming": "Algorithms",
            "greedy": "Algorithms",
            "class": "OOP",
            "object": "OOP",
            "inheritance": "OOP",
            "polymorphism": "OOP",
            "encapsulation": "OOP",
            "function": "Programming Basics",
            "variable": "Programming Basics",
            "loop": "Programming Basics",
            "loops": "Programming Basics",
            "conditional": "Programming Basics",
            "sql": "Databases",
            "query": "Databases",
            "neural network": "Artificial Intelligence",
            "deep learning": "Machine Learning",
        }
        
        # Add direct questions about specific concepts
        direct_concept_questions = {
            "what is linked list": ("Data Structures", "linked_list"),
            "what is a linked list": ("Data Structures", "linked_list"),
            "what is link list": ("Data Structures", "linked_list"),
            "what is a link list": ("Data Structures", "linked_list"),
            "explain linked list": ("Data Structures", "linked_list"),
            "define linked list": ("Data Structures", "linked_list"),
        }
        
        # Check for direct concept questions first
        for pattern, (topic, subtopic) in direct_concept_questions.items():
            if pattern in question:
                return topic, subtopic
        
        # First, let's check for special terms like 'loops' which need priority
        # These are terms that might appear in multiple topics but have specific meanings
        priority_concepts = {
            "loop": "Programming Basics",
            "loops": "Programming Basics",
            "for loop": "Programming Basics",
            "while loop": "Programming Basics",
            "do while": "Programming Basics",
            "iteration": "Programming Basics"
        }
        
        for concept, related_topic in priority_concepts.items():
            if concept in question and related_topic in self.knowledge_base:
                return related_topic, "definition"
        
        # Extract topic - check if any known topic is mentioned
        topic = None
        for t in self.topics:
            if t.lower() in question:
                topic = t
                break
        
        # Check for common CS concepts if no topic was found
        if topic is None:
            for concept, related_topic in cs_concepts.items():
                if concept in question and related_topic in self.knowledge_base:
                    return related_topic, "definition"
        
        # If no known topic found and web search is enabled, 
        # extract potential CS topics using keywords
        if topic is None and self.use_web_search:
            cs_keywords = [
                "algorithm", "data structure", "programming", "software", "database", 
                "network", "operating system", "computer", "artificial intelligence", 
                "machine learning", "web development", "cybersecurity", "cloud computing",
                "big data", "blockchain", "internet of things", "iot", "compiler", 
                "computer vision", "nlp", "natural language processing", "cryptography",
                "distributed systems", "parallel computing", "quantum computing", "robotics",
                "array", "list", "stack", "queue", "tree", "graph", "hash table", "linked list",
                "sorting", "searching", "recursion", "class", "object", "inheritance", "function",
                "variable", "loop", "loops", "sql", "query", "neural network", "deep learning"
            ]
            
            for keyword in cs_keywords:
                if keyword in question:
                    # Use the keyword phrase as potential topic
                    topic = keyword
                    break
        
        # Determine intent
        intents = {
            "definition": ["what is", "what are", "define", "explain", "mean by", "definition of", "tell me about", "how will you define"],
            "concepts": ["concepts", "principles", "ideas", "fundamentals", "basics of"],
            "examples": ["example", "application", "use case", "practical", "instance of"],
            "related": ["related", "similar", "next", "after", "other", "more topics"]
        }
        
        intent = "definition"  # Default intent
        for intent_type, keywords in intents.items():
            if any(keyword in question for keyword in keywords):
                intent = intent_type
                break
        
        return topic, intent
    
    def _search_web(self, query: str) -> str:
        """
        Search the web for information using a web search API.
        
        For a production application, you would integrate with a robust API like:
        1. Google Custom Search API
        2. Bing Search API
        3. SerpAPI
        
        Args:
            query: The search query
            
        Returns:
            Information found on the web
        """
        try:
            print(f"Searching for: {query}")
            
            # APPROACH 1: REAL API INTEGRATION (commented out for demo)
            # For a real-world implementation, uncomment and configure with your API keys
            
            # # Google Custom Search API example
            # GOOGLE_API_KEY = "YOUR_API_KEY"  # In production, use environment variables
            # GOOGLE_CSE_ID = "YOUR_CSE_ID"    # In production, use environment variables
            # url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
            # response = requests.get(url)
            # if response.status_code == 200:
            #     data = response.json()
            #     if "items" in data and len(data["items"]) > 0:
            #         result = data["items"][0]["snippet"]
            #         source = data["items"][0]["link"]
            #         return f"{result} [Source: {source}]"
            
            # APPROACH 2: SIMULATE API WITH KNOWLEDGE BASE
            
            # Knowledge base simulation - this would be expanded dramatically in a real app
            # or replaced with a vector database for more sophisticated retrieval
            knowledge_base = {
                "quantum computing": """Quantum computing is a type of computing that uses quantum phenomena such as superposition and entanglement to perform operations on data. 
                While traditional computers store information in binary form (0s and 1s), quantum computers use quantum bits or 'qubits' that can exist in multiple states simultaneously.
                This allows quantum computers to solve certain problems much faster than classical computers, particularly in areas like cryptography, optimization, and simulation of quantum systems.
                Quantum computing is still largely in experimental stages, with companies like IBM, Google, and Microsoft making significant investments in the technology.""",
                
                "blockchain": """Blockchain is a distributed ledger technology that maintains a continuously growing list of records (blocks) that are linked and secured using cryptography.
                Each block contains a timestamp, transaction data, and a reference to the previous block, making the data tamper-resistant.
                Blockchain is the underlying technology for cryptocurrencies like Bitcoin, but has applications beyond digital currencies, including supply chain management, voting systems, and smart contracts.
                Its key features include decentralization, transparency, and immutability.""",
                
                "serverless": """Serverless computing is a cloud computing execution model where the cloud provider dynamically manages the allocation of machine resources.
                Despite the name, servers are still used, but developers don't need to worry about server management.
                Applications are broken down into individual functions that can be invoked and scaled individually.
                Benefits include reduced operational costs (pay-per-execution), automatic scaling, and decreased system complexity.
                Popular serverless platforms include AWS Lambda, Azure Functions, and Google Cloud Functions.""",
                
                "machine learning": """Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.
                It focuses on the development of algorithms that can analyze and learn from data, identify patterns, and make decisions with minimal human intervention.
                Common types include supervised learning (training with labeled data), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through reward/penalty feedback).
                Applications include recommendation systems, fraud detection, natural language processing, computer vision, and autonomous vehicles.""",
                
                "internet of things": """The Internet of Things (IoT) refers to the network of physical objects embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices and systems over the internet.
                These devices range from ordinary household objects to sophisticated industrial tools, and can include everything from fitness trackers to smart home systems and industrial sensors.
                IoT enables seamless communication between people, processes, and things, creating opportunities for more direct integration of the physical world into computer-based systems.
                This integration can result in improved efficiency, economic benefits, and reduced human exertion.""",
                
                "artificial intelligence": """Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems.
                These processes include learning (acquiring information and rules for using it), reasoning (using rules to reach approximate or definite conclusions), and self-correction.
                AI encompasses various subfields including machine learning, deep learning, natural language processing, computer vision, and robotics.
                It has applications across numerous industries including healthcare, finance, transportation, entertainment, and education.""",
                
                "deep learning": """Deep learning is a subset of machine learning based on artificial neural networks with multiple layers (hence "deep").
                These neural networks attempt to simulate the behavior of the human brain—albeit far from matching its ability—allowing it to "learn" from large amounts of data.
                Deep learning excels at identifying patterns in unstructured data like images, sound, text, and video.
                It powers many technologies we use today, including voice assistants, translation services, facial recognition systems, and autonomous vehicles.""",
                
                "cybersecurity": """Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks, damage, or unauthorized access.
                These attacks typically aim to access, change, or destroy sensitive information, extort money from users, or interrupt normal business processes.
                Effective cybersecurity employs multiple layers of protection spread across computers, networks, programs, and data.
                Key areas include network security, application security, information security, operational security, disaster recovery, and end-user education.""",
                
                "virtual reality": """Virtual Reality (VR) is a simulated experience that can be similar to or completely different from the real world.
                It immerses users in a fully artificial digital environment, typically experienced through a headset that tracks head movements.
                Applications of VR include entertainment (particularly video games), education (such as medical or military training), and business (such as virtual meetings).
                The technology continues to evolve, with improvements in display resolution, field of view, haptic feedback, and motion tracking.""",
                
                "augmented reality": """Augmented Reality (AR) is an interactive experience that enhances the real world with computer-generated perceptual information.
                Unlike Virtual Reality, which replaces the real world with a simulated one, AR adds digital elements to a live view, often by using the camera on a smartphone or special headsets.
                AR applications include navigation systems, gaming (like Pokémon GO), retail (virtual try-on), industrial (maintenance and repair guidance), and education.
                The technology combines real and virtual worlds, is interactive in real-time, and registers virtual objects in 3D.""",
                
                "cloud computing": """Cloud computing is the delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet ("the cloud").
                It offers faster innovation, flexible resources, and economies of scale, typically with a pay-as-you-go pricing model.
                Main service models include Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS).
                Major providers include Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform, and IBM Cloud.""",
                
                "data science": """Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data.
                It combines aspects of statistics, data analysis, mathematics, computer science, and domain expertise to interpret data for decision-making.
                The data science workflow typically includes data collection, cleaning, exploration, modeling, and communication of results.
                Applications span virtually every industry, from healthcare and finance to marketing and transportation.""",
                
                "edge computing": """Edge computing is a distributed computing paradigm that brings computation and data storage closer to the location where it is needed.
                This reduces latency and bandwidth use, improving response times and saving bandwidth, which is particularly important for Internet of Things (IoT) applications.
                Rather than sending all data to a central data center or cloud, edge computing processes data locally on edge devices or nearby edge servers.
                Applications include smart cities, autonomous vehicles, industrial IoT, and content delivery networks.""",
            }
            
            # Get the most relevant key based on the query
            best_key = None
            max_relevance = 0
            
            for key in knowledge_base.keys():
                if key in query.lower():
                    return knowledge_base[key]
                
                # Calculate relevance score based on word overlap
                query_words = set(query.lower().split())
                key_words = set(key.split())
                overlap = len(query_words.intersection(key_words))
                
                if overlap > max_relevance:
                    max_relevance = overlap
                    best_key = key
            
            # If we found a reasonably relevant topic (at least one word matches)
            if max_relevance > 0:
                return knowledge_base[best_key]
            
            # APPROACH 3: FALLBACK TO PUBLIC API (limited but doesn't require API key)
            
            # Try to get basic information from DuckDuckGo API
            encoded_query = query.replace(" ", "+")
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("Abstract"):
                    return data.get("Abstract")
                elif data.get("RelatedTopics") and len(data.get("RelatedTopics")) > 0:
                    return data.get("RelatedTopics")[0].get("Text", "No information found.")
            
            # If we reach here, no information was found
            return f"""I don't have specific information about "{query}" in my knowledge base. 
            In a production system, this would connect to a search API to find real-time information.
            Try asking about computer science topics like algorithms, data structures, programming languages, 
            or technologies like machine learning, cloud computing, blockchain, or cybersecurity."""
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return f"""I encountered an error while searching for information about "{query}".
            In a real production system, this would be connected to a robust search API.
            For now, try asking about topics I have in my knowledge base like data structures, 
            algorithms, programming basics, or specific technologies."""
    
    def generate_response(self, question: str) -> str:
        """
        Generate a response based on the user's question.
        
        Args:
            question: The user's question
            
        Returns:
            Chatbot response
        """
        # Check for greeting
        greetings = ["hello", "hi", "hey", "greetings", "sup", "what's up"]
        if any(greeting in question.lower() for greeting in greetings):
            return random.choice(self.templates["greeting"])
        
        # Check for thanks
        thanks_keywords = ["thanks", "thank you", "appreciate", "helpful", "great"]
        if any(keyword in question.lower() for keyword in thanks_keywords):
            return random.choice(self.templates["thanks"])
        
        # Special handling for common direct questions about CS concepts
        direct_questions = {
            "what is an array": "An array is a fundamental data structure that stores elements of the same type in contiguous memory locations. It allows efficient access to elements using indices and is the foundation for many more complex data structures.",
            "how will you define loops": "Loops are control flow structures in programming that allow repeated execution of a block of code. The main types are for loops (which iterate a specific number of times), while loops (which continue until a condition is false), and do-while loops (which execute at least once).",
            "what are loops": "Loops are programming constructs that execute a block of code repeatedly based on a condition. Common types include for loops, while loops, and do-while loops. They're essential for tasks like iterating through arrays, processing collections of data, or repeating operations until a specific condition is met.",
            "define loops": "Loops are control flow statements that allow code to be executed repeatedly based on a given condition. They're fundamental to programming and are used when you need to perform the same action multiple times with different data or until a certain condition changes.",
            "what is linked list": "A linked list is a linear data structure where elements are stored in nodes, and each node points to the next node in the sequence. Unlike arrays, linked lists don't require contiguous memory; each node can be stored anywhere in memory. Linked lists allow efficient insertion and deletion operations but don't provide direct access to elements (requiring O(n) traversal).",
            "what is a linked list": "A linked list is a linear data structure where elements are stored in nodes, and each node points to the next node in the sequence. Unlike arrays, linked lists don't require contiguous memory; each node can be stored anywhere in memory. Linked lists allow efficient insertion and deletion operations but don't provide direct access to elements (requiring O(n) traversal).",
            "what is link list": "A linked list is a linear data structure where elements are stored in nodes, and each node points to the next node in the sequence. Unlike arrays, linked lists don't require contiguous memory; each node can be stored anywhere in memory. Linked lists allow efficient insertion and deletion operations but don't provide direct access to elements (requiring O(n) traversal).",
            "what is quantum computing": "Quantum computing is a type of computing that uses quantum phenomena such as superposition and entanglement to perform operations on data. While traditional computers store information in binary form (0s and 1s), quantum computers use quantum bits or 'qubits' that can exist in multiple states simultaneously. This allows quantum computers to solve certain problems much faster than classical computers, particularly in cryptography, optimization, and simulation of quantum systems.",
            "what is quantum computing?": "Quantum computing is a type of computing that uses quantum phenomena such as superposition and entanglement to perform operations on data. While traditional computers store information in binary form (0s and 1s), quantum computers use quantum bits or 'qubits' that can exist in multiple states simultaneously. This allows quantum computers to solve certain problems much faster than classical computers, particularly in cryptography, optimization, and simulation of quantum systems."
        }
        
        # Check if the question matches any direct question patterns
        question_lower = question.lower().strip()
        for pattern, response in direct_questions.items():
            if pattern in question_lower or question_lower in pattern:
                return response
        
        # Identify topic and intent
        topic, intent = self._identify_topic_and_intent(question)
        
        # Print debug info to help diagnose issues (can be removed in production)
        print(f"Debug - Question: {question}, Identified Topic: {topic}, Intent: {intent}")
        
        # Handle known topics from knowledge base
        if topic in self.knowledge_base:
            # Get content based on intent
            if intent in self.knowledge_base[topic]:
                content = self.knowledge_base[topic][intent]
            else:
                # Fallback to definition if the specific intent isn't available
                content = self.knowledge_base[topic].get("definition", 
                         f"I don't have specific {intent} information about {topic}.")
            
            # Generate response using template
            template = random.choice(self.templates[intent])
            return template.format(topic=topic, content=content)
        
        # Handle unknown topics with web search if enabled
        elif topic is not None and self.use_web_search:
            # Create a search query based on the intent and topic
            search_query = question
            if intent == "definition":
                search_query = f"What is {topic} in computer science"
            elif intent == "concepts":
                search_query = f"Main concepts of {topic} in computer science"
            elif intent == "examples":
                search_query = f"Examples of {topic} in computer science"
            elif intent == "related":
                search_query = f"Topics related to {topic} in computer science"
            
            # Perform web search
            web_result = self._search_web(search_query)
            
            # Generate response using template
            template = random.choice(self.templates["web_search"])
            return template.format(content=web_result)
        
        # No relevant information found
        else:
            return random.choice(self.templates["not_found"]).format(topics=", ".join(self.topics))


# Expanded knowledge base for CS topics
def get_extended_knowledge_base():
    """
    Get an extended knowledge base covering a wider range of CS topics.
    """
    # Start with the sample knowledge base
    kb = get_sample_knowledge_base()
    
    # Add supplementary information for Data Structures
    data_structures = kb.get("Data Structures", {})
    data_structures.update({
        "linked_list_types": "There are several types of linked lists: 1) Singly Linked List - each node points to the next node, 2) Doubly Linked List - each node points to both next and previous nodes, 3) Circular Linked List - the last node points back to the first node.",
        "linked_list_operations": "Common operations on linked lists include: insertion (at beginning, end, or middle), deletion, traversal, searching, and reversal. Most operations have O(1) time complexity at the beginning, but may require O(n) time if performed elsewhere in the list.",
        "linked_list_advantages": "Advantages of linked lists include: dynamic size (can grow or shrink during execution), efficient insertions and deletions, and no need for contiguous memory allocation.",
        "linked_list_disadvantages": "Disadvantages of linked lists include: extra memory for storing pointers, no random access (must traverse from beginning), complex implementation compared to arrays, and potential cache miss issues due to non-contiguous memory."
    })
    kb["Data Structures"] = data_structures
    
    # Add more CS topics
    kb.update({
        "Artificial Intelligence": {
            "definition": "The field of computer science focused on creating systems that can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and translation.",
            "concepts": "Machine learning, neural networks, natural language processing, expert systems, robotics, computer vision, and knowledge representation.",
            "examples": "Building a chess-playing AI, creating a facial recognition system, developing a language translation service.",
            "related": "Machine Learning, Computer Vision, Natural Language Processing"
        },
        "Machine Learning": {
            "definition": "A subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
            "concepts": "Supervised learning, unsupervised learning, reinforcement learning, neural networks, decision trees, and feature engineering.",
            "examples": "Training a model to detect spam emails, clustering customers based on purchasing behavior, teaching an AI to play video games through reinforcement.",
            "related": "Artificial Intelligence, Deep Learning, Data Science"
        },
        "Web Development": {
            "definition": "The process of creating websites and web applications for the internet or intranet.",
            "concepts": "HTML, CSS, JavaScript, front-end frameworks, back-end programming, APIs, databases, and responsive design.",
            "examples": "Building an e-commerce website, creating a social media platform, developing a blog with a content management system.",
            "related": "Frontend Development, Backend Development, Databases"
        },
        "Cybersecurity": {
            "definition": "The practice of protecting systems, networks, and programs from digital attacks aimed at accessing, changing, or destroying sensitive information.",
            "concepts": "Encryption, authentication, authorization, firewalls, intrusion detection, vulnerability assessment, and security policy.",
            "examples": "Implementing a secure authentication system, conducting penetration testing, setting up a network firewall.",
            "related": "Cryptography, Network Security, Ethical Hacking"
        },
        "Computer Networks": {
            "definition": "A collection of computers and devices interconnected by communication channels that allow sharing of resources and information.",
            "concepts": "TCP/IP, OSI model, routing, switching, network topologies, protocols, and network security.",
            "examples": "Setting up a LAN for a small office, configuring a wireless network, implementing a VPN for secure remote access.",
            "related": "Internet, Cybersecurity, Distributed Systems"
        },
        "Software Engineering": {
            "definition": "The systematic application of engineering approaches to the development of software.",
            "concepts": "Software development lifecycle, requirements analysis, design patterns, testing, version control, agile methodologies, and DevOps.",
            "examples": "Creating a software development plan, designing a modular application architecture, implementing continuous integration/deployment.",
            "related": "Programming, Project Management, Quality Assurance"
        },
        "Computer Graphics": {
            "definition": "The field concerned with digitally synthesizing and manipulating visual content.",
            "concepts": "Rasterization, ray tracing, 3D modeling, animation, rendering, shading, and texture mapping.",
            "examples": "Creating 3D models for video games, designing special effects for movies, developing visualization tools for scientific data.",
            "related": "Computer Vision, Animation, Virtual Reality"
        },
        "Cloud Computing": {
            "definition": "The delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet.",
            "concepts": "Infrastructure as a Service (IaaS), Platform as a Service (PaaS), Software as a Service (SaaS), virtualization, containerization, and cloud security.",
            "examples": "Deploying applications on AWS, storing data in Google Cloud, setting up a virtual private cloud for a company.",
            "related": "Distributed Systems, Virtualization, Serverless Computing"
        }
    })
    
    # Add supplementary information for existing topics
    programming_basics = kb.get("Programming Basics", {})
    programming_basics.update({
        "control_structures": "Control structures direct the flow of execution in a program. The three main types are sequence (executing statements in order), selection (if-else, switch statements), and iteration (loops).",
        "for_loop": "A for loop executes a block of code a specified number of times. It typically consists of an initialization, a condition, and an increment/decrement step. For loops are ideal when you know in advance how many times you need to iterate.",
        "while_loop": "A while loop executes a block of code as long as a specified condition is true. The condition is evaluated before each iteration, so if it's initially false, the loop body won't execute at all.",
        "do_while_loop": "A do-while loop is similar to a while loop, but the condition is checked after the loop body executes. This guarantees that the loop body executes at least once, regardless of the condition.",
        "iteration": "Iteration is the process of repeatedly executing a block of code. Loops are the primary means of implementing iteration in programming. Iteration is essential for processing collections of data, implementing algorithms, and automating repetitive tasks."
    })
    kb["Programming Basics"] = programming_basics
    
    return kb


# Sample knowledge base for CS topics (original function preserved for compatibility)
def get_sample_knowledge_base():
    return {
        "Programming Basics": {
            "definition": "The fundamental concepts and techniques of computer programming, including variables, control structures, functions, and basic algorithms.",
            "concepts": "Variables, data types, operators, loops, conditionals, functions, and basic I/O operations.",
            "examples": "Writing a program to calculate factorial, creating a simple calculator, implementing a temperature converter.",
            "related": "Data Structures, Algorithms, OOP",
            "loops": "Loops are control flow structures that allow code to be executed repeatedly. Common types include: 1) For loops - execute a block of code a fixed number of times, 2) While loops - execute as long as a condition is true, 3) Do-while loops - execute at least once and then as long as a condition is true. Loops are essential for tasks like iterating through collections, processing data, and implementing algorithms."
        },
        "Data Structures": {
            "definition": "Ways to organize and store data in computer memory for efficient access and modification.",
            "concepts": "Arrays, linked lists, stacks, queues, trees, graphs, hash tables, and heaps.",
            "examples": "Implementing a linked list to manage a collection, using a stack to evaluate expressions, employing a hash table for fast lookups.",
            "related": "Algorithms, Programming Basics, OOP",
            "array": "An array is a fundamental data structure that stores elements of the same type in contiguous memory locations. Elements can be accessed using indices, which allow O(1) constant-time access. Arrays are fixed-size in most low-level languages, though dynamic arrays can grow automatically.",
            "linked_list": "A linked list is a linear data structure where elements are stored in nodes, and each node points to the next node in the sequence. Unlike arrays, linked lists don't require contiguous memory; each node can be stored anywhere in memory. Linked lists allow efficient insertion and deletion operations but don't provide direct access to elements (requiring O(n) traversal). Types include singly linked lists (nodes point to next node), doubly linked lists (nodes point to both next and previous), and circular linked lists (last node points back to first)."
        },
        "Algorithms": {
            "definition": "Step-by-step procedures or formulas for solving problems, particularly calculations and data processing tasks.",
            "concepts": "Sorting algorithms, searching algorithms, graph algorithms, greedy algorithms, dynamic programming, and complexity analysis.",
            "examples": "Implementing quicksort to arrange elements, using binary search to find an item, applying Dijkstra's algorithm to find shortest paths.",
            "related": "Data Structures, Operating Systems"
        },
        "OOP": {
            "definition": "Object-Oriented Programming is a programming paradigm based on the concept of 'objects' containing data and methods.",
            "concepts": "Classes, objects, inheritance, polymorphism, encapsulation, and abstraction.",
            "examples": "Creating a class hierarchy for different shapes, implementing a banking system with accounts and transactions, designing a game with various character types.",
            "related": "Programming Basics, Design Patterns, Software Engineering"
        },
        "Databases": {
            "definition": "Systems designed to store, retrieve, and manage large amounts of data, often with support for querying and manipulation.",
            "concepts": "Relational databases, SQL, NoSQL, tables, queries, normalization, transactions, and ACID properties.",
            "examples": "Creating a database for a library management system, designing schemas for an e-commerce platform, optimizing queries for a social media application.",
            "related": "Data Structures, Operating Systems"
        },
        "Operating Systems": {
            "definition": "Software that manages computer hardware and software resources and provides common services for computer programs.",
            "concepts": "Process management, memory management, file systems, I/O management, virtualization, and security.",
            "examples": "Implementing a simple scheduler, designing a memory allocator, creating a basic file system.",
            "related": "Computer Architecture, Networks, Databases"
        }
    } 
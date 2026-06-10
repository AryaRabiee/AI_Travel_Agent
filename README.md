# 🧳 AI Travel Assistant (RAG-based)

An AI-powered travel assistant that helps users discover cities, generate personalized travel plans, and get real-time travel information through a conversational interface.

This project uses **LLMs, RAG architecture, vector search, and stateful conversation management** to simulate an intelligent travel planning experience.

---

## 🚀 Features

### 🧠 Intelligent Conversation System
- Multi-turn dialogue with state management
- Handles travel workflows step-by-step
- Dynamic context switching (weather, planning, city info, comparison)

### 🗺️ Travel Planning
- Personalized travel itinerary generation
- Profile-based recommendation system
- Multi-day travel planning support

### 🌦️ Weather Assistant
- Real-time weather queries per city
- Travel suitability analysis
- Offline fallback responses for reliability

### 🏙️ City Intelligence (RAG System)
- City knowledge retrieval system
- Uses json-based city documents
- Context-aware city Q&A

### ⚖️ City Comparison
- Compare two cities based on user intent
- Travel decision assistance

### 🔍 Intent Classification System
- LLM-based routing system
- Extracts:
  - intent
  - city
  - number of days
  - travel goals
- Supports multi-turn conversation awareness

### 🧩 Robust Architecture
- Multi-model fallback (OpenRouter-based)
- State machine for conversation flow
- Error-handling and safe responses

---

## 🏗️ System Architecture
User Message
↓
Intent Classifier (LLM)
↓
State Manager (Conversation State)
↓
Router (Weather / Plan / City Info / Compare)
↓
RAG Layer (City Docs + Vector Search) or API for weather
↓
LLM Response Generator


---

## 🧠 Tech Stack

- Python 🐍
- FastAPI ⚡
- LLMs (OpenRouter API)
- RAG (Retrieval-Augmented Generation)
- Vector Database (Embeddings-based search)
- API for weather

---

## 📦 Installation

### 1. Clone repository
```bash
git clone https://github.com/AryaRabiee/AI_Travel_Agent.git
cd app
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
Create .env file:
OPENROUTER_API_KEY=your_api_key
WEATHER_API_KEY=your_api_key
fastapi dev main.py
```
### 🐳 Docker Setup
docker build -t travel-assistant .
docker run -p 8000:8000 --env-file .env travel-assistant
---

### ⚠️Limitations (v1.0)
Supports limited number of cities (6 cities)
Weather depends on external API
Intent classification may fail in ambiguous cases (~80–85% accuracy)
No flight/hotel booking integration yet
No real-time pricing system

---
### 🧪 Future Improvements
Integration with flight & hotel APIs
Better intent model (fine-tuned classifier)
Evaluation system for RAG responses
Memory optimization (long-term user profile memory)
Scaling vector database for more cities
Advanced caching layer

### ⭐ If you like this project

Give it a star ⭐ on GitHub and feel free to contribute or fork it.


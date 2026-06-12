# 🧳 AI Travel Assistant

AI Travel Assistant is an LLM-powered travel planning system that helps users discover destinations, compare cities, retrieve travel information, check weather conditions, and generate personalized travel itineraries through a conversational interface.

Unlike a traditional chatbot, this project combines:

* Intent Classification
* Stateful Conversation Management
* Retrieval-Augmented Generation (RAG)
* Vector Search
* Multi-model LLM Fallback
* Personalized Travel Recommendation

to create a more reliable and context-aware travel assistant.

The goal of this project is to explore real-world AI Engineering concepts such as routing, RAG pipelines, conversation state management, retrieval systems, prompt engineering, and production-oriented LLM application design.

---
# 🎬 Demo

![Demo](assets/demo.gif)


# 🎬 Demo

![Demo](assets/demo.gif)


# 🚀 Features

## Intelligent Conversation System

* Multi-turn dialogue support
* Conversation state management
* Context-aware responses
* Workflow handling for travel planning

## Travel Recommendation Engine

* User profile generation
* Personalized destination recommendation
* Travel preference analysis

## Travel Plan Generation

* Multi-day itinerary generation
* Personalized planning based on user profile

## City Information Retrieval (RAG)

* Retrieval-based city knowledge system
* Context-aware city question answering
* Grounded responses using local knowledge base

## Weather Assistant

* Real-time weather retrieval
* Travel suitability analysis
* Offline fallback support

## City Comparison

* Compare multiple destinations
* Travel decision assistance

## Reliability Features

* Multi-model fallback strategy
* Basic error handling
* Offline weather fallback
* State recovery mechanisms

---

# 🏗️ System Architecture

```text
User Message
      │
      ▼
Intent Classifier
      │
      ▼
Conversation State Manager
      │
      ▼
Router
 ┌────┼────┬─────┬─────┐
 ▼    ▼    ▼     ▼     ▼
Weather City Plan Compare NormalChat
   │     │    │      │      │
   │     │    │      │      └──────────┐
   │     │    │      │                 │
   └─────┴────┴──────┘                 │
            │                          │
            ▼                          ▼
      RAG / APIs              LLM Response Generator
            │                          ▲
            └──────────────────────────┘
```

---

# 📂 Project Structure

```text
AI_Travel_Agent/
├── app/
│   ├── main.py
│   │
│   ├── md_to_embeddings.py
|   | 
│   ├── llm/
│   │   ├── client.py
│   │   ├── model_manager.py
│   │   ├── travel_plan.py
│   │   └── log.py
│   │
│   ├── rag/
│   │   ├── retrieval.py
│   │   ├── vector_search.py
│   │   └── embeddings.py
│   │   
│   │
│   ├── router/
│   │   ├── intent.py
│   │   └── weather_intent.py
│   │   
│   │   
│   │
│   ├── state/
│   │   ├── handel_user.py
│   │   ├── memory.py
│   │   ├── save_answer.py
│   │   ├── state_user.py
│   │   ├── travel_question_step.py
│   │   └── validation.py
│   │
│   ├── CBF_Recommendation/
│   │   ├── city_matrix.py
│   │   ├── model_weight.py
│   │   └── recommandation_score.py
│   
│
├── data/
├── requirements.txt
└── README.md
```

## Important Files

### main.py

Application entry point and FastAPI server.

### intent.py

Intent classification and entity extraction.


### weather_intent.py

Weather retrieval and weather-response generation.

### data/

Local city knowledge base used by the RAG system.



---

# 🧠 Tech Stack

* Python
* FastAPI
* OpenRouter API
* RAG
* Vector Database(faiss)
* Embeddings
* Docker

---

# ⚙️ Installation

```bash
git clone https://github.com/AryaRabiee/AI_Travel_Agent.git

cd AI_Travel_Agent

python -m venv venv

# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env`

```env
OPENROUTER_API_KEY=your_api_key
WEATHER_API_KEY=your_api_key
```

Run:

```bash
fastapi dev main.py
```

---

# 🐳 Docker

Build image:

```bash
docker build -t travel-assistant .
```

Run container:

```bash
docker run -p 8000:8000 --env-file .env travel-assistant
```

---

# ⚠️ Current Limitations

* Supports a limited number of cities
* No flight booking integration
* No hotel booking integration
* Intent classification is currently based on prompting and may occasionally misclassify ambiguous user requests.
* No long-term memory

---

# 🧪 Future Improvements

* Improve intent classification accuracy and ambiguity handling
* Add city-to-city distance calculation
* Recommend transportation methods (car, train, flight)
* Retrieve attraction addresses and location information
* Integrate weather-aware travel recommendations
* Expand city knowledge base and tourism data
* Evaluation framework for RAG quality assessment
* Advanced memory management
* Response caching layer
* Production monitoring and observability



---

# ⭐ Project Status

Current Version: **v1.0.0**

This version represents the first stable release of the AI Travel Assistant.

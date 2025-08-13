<h1 align="center">Multi-Agentic Health Assistant</h1>
<p align="center">A comprehensive wellness platform powered by AI agents for personalised health management.</p>

<hr />
<p align="center">
  <img src="web_files/virtualhealth.png" alt="Virtual Health Assistant" >
</p>

## 📋 Overview

The Multi-Agentic Health Assistant is an innovative wellness platform that combines the power of multiple Large Language Models (LLMs) and vision models to provide personalized support for physical and mental well-being. The system integrates three specialised AI agents that work together to deliver comprehensive health management through diet tracking, exercise planning, and mental health support.

## 🏗️ System Architecture

The platform utilises a multi-agent architecture with three specialised LLM agents, each designed for specific health domains:

### 🧠 Mental Health Agent
**Knowledge-based system** for emotional support and mental wellness.

- Daily check-ins and emotional support
- Guided journaling and motivational prompts
- Sentiment analysis and emotion classification
- Secure conversation memory with a flagging system
- Long-term interaction tracking

### 🥗 Diet Agent
**Vision-enabled system** for nutrition analysis and meal planning.

- Meal planning and nutritional suggestions
- Vision-based analysis of food photos
- Nutrient breakdown and diet goal comparison
- Dietary preference accommodation
- Calorie and macro tracking

### 💪 Exercise Agent
**Database-driven system** for fitness planning and tracking.

- Personalised workout routine generation
- Workout completion and calorie tracking
- Weekly difficulty and goal adjustments
- Performance data logging
- Progress monitoring and analytics

## 🌟 Key Features

**Unified Web Interface:** Streamlit/Flask based frontend with intuitive navigation  
**Multi-Modal AI:** Integration of text and vision models for comprehensive analysis  
**Personalised Recommendations:** Tailored advice based on individual profiles and goals  
**Persistent Memory:** Secure storage of user interactions and progress  
**Real-time Analysis:** Instant feedback on meals, workouts, and mental health  
**Privacy-Focused:** Secure data handling with user control over information  

## 🔧 Tech Stack

- **Text Model:** DeepSeek V3 671B Text
- **Vision Model:** LLaMA 3.2 11B Vision
- **Frontend:** Streamlit/Flask
- **Database:** PostgreSQL & Pinecone
- **API:** Together.ai
- **Language:** Python 3.12.7

## 🚀 Getting Started

### Prerequisites

- Python 3.12.7 or higher
- [together.ai](https://www.together.ai/) API key 
- Basic understanding of health and wellness concepts

## Installation
#### The project has 2 branches:
- One was built with Streamlit to a certain point and incorporates only 1 agent and a faulty UI; this branch was abandoned. <a href="https://virtualhealth.streamlit.app/">View Here</a> <br>
- The second branch is built with Flask, HTML, CSS, and Vanilla JS. It has a desirable UI and incorporates the agents properly, and is built to a much better extent than the other branch. <a href="https://multi-agentic-health-assistant.onrender.com">View Here</a>

1. **Clone the repository:**
```bash
git clone https://github.com/ib-hussain/Multi-Agentic_Health_Assistant
cd Multi-Agentic_Health_Assistant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
Branch -> main:
streamlit run website.py
Hosted at: https://virtualhealth.streamlit.app/
or
Branch -> flask:
python app.py
Hosted at: https://multi-agentic-health-assistant.onrender.com
```


## 📱 User Interface

The web interface includes 5 main sections:

- **Login:** Login to your account.
- **Signup:** Give the AI your details.
- **Chatbot:** Talk to the Agentic-AI regarding your daily diet, excercises and mental health.
- **Profile Management:** View or change your user details from this page as well as logout of your account.
- **Daily Progress Tracking:** Workout logging and routine management.

## 🔮 Advanced Features

### Token and History Management
- Rolling window context management for each LLM
- Automatic summarisation of older conversations
- Long-term memory specifically for mental health continuity

### Audio Integration
- Voice communication with AI agents
- Real-time transcription and response
- Hands-free interaction capability


## 📄 License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the code, but the original ownership and attribution must be maintained. See the [LICENSE](LICENSE) file for details.



## 👨‍💻 Project Maintainer

This project is maintained and owned by **Ibrahim Hussain**

For questions, suggestions, or collaboration opportunities, feel free to reach out!

---
<p align="center"><i>Built for better health and wellness | © 2025 Multi-Agentic Health Assistant</i></p>

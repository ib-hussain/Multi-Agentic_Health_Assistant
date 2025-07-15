<h1 align="center">Multi-Agentic Health Assistant</h1>
<p align="center">A comprehensive wellness platform powered by AI agents for personalised health management.</em></p>

<hr />

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![AI](https://img.shields.io/badge/AI-LLaMA%203.1-purple.svg)

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

✅ **Unified Web Interface:** Streamlit-based frontend with intuitive navigation  
✅ **Multi-Modal AI:** Integration of text and vision models for comprehensive analysis  
✅ **Personalised Recommendations:** Tailored advice based on individual profiles and goals  
✅ **Persistent Memory:** Secure storage of user interactions and progress  
✅ **Real-time Analysis:** Instant feedback on meals, workouts, and mental health  
✅ **Privacy-Focused:** Secure data handling with user control over information  

## 🔧 Tech Stack

- **Text Model:** LLaMA 3.1 8B
- **Vision Model:** LLaMA 3.2 11B Vision
- **Frontend:** Streamlit
- **Database:** SQLite/PostgreSQL
- **API:** Together.ai
- **Language:** Python 3.8+

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Together.ai API key (get $1 free credit at [together.ai](https://www.together.ai/))
- Basic understanding of health and wellness concepts

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ib-hussain/Multi-Agentic_Health_Assistant
cd multi-agentic-health-assistant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your API key:**
```bash
export TOGETHER_API_KEY="your-api-key-here"
```

4. **Initialise the database:**
```bash
python setup_db.py
```

5. **Run the application:**
```bash
streamlit run app.py
```

> 💡 **Pro Tip:** The $1 credit from Together.ai should be sufficient for testing and initial development. The system is designed to be cost-effective while maintaining high performance.

## 📱 User Interface

The web interface includes four main sections:

- **Dashboard:** Overview of health metrics and daily progress
- **Mental Health:** Chat interface with memory toggle for session continuity
- **Diet Tracker:** Photo upload and analysis with nutritional breakdowns
- **Exercise Plan:** Workout logging and routine management

## 🔮 Advanced Features

### Token and History Management
- Rolling window context management for each LLM
- Automatic summarisation of older conversations
- Long-term memory specifically for mental health continuity

### Audio Integration
- Voice communication with AI agents
- Real-time transcription and response
- Hands-free interaction capability


## ⚠️ Important Notice

This system is designed for wellness support and should not replace professional medical advice. Always consult healthcare professionals for serious health concerns.

## 📄 License

This project is licensed under the MIT License. This means you are free to use, modify, and distribute the code, but the original ownership and attribution must be maintained. See the [LICENSE](LICENSE) file for details.



## 👨‍💻 Project Maintainer

This project is maintained and owned by **Ibrahim Hussain**

For questions, suggestions, or collaboration opportunities, feel free to reach out!

---

*Built for better health and wellness | © 2025 Multi-Agentic Health Assistant*

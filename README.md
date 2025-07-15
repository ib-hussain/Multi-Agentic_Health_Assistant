<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agentic Health Assistant</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        h1 {
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.2em;
            margin-bottom: 30px;
            font-style: italic;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 40px;
        }
        
        h3 {
            color: #2980b9;
            margin-top: 30px;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 12px;
            margin: 5px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            text-decoration: none;
            transition: transform 0.2s;
        }
        
        .badge:hover {
            transform: translateY(-2px);
        }
        
        .badge-license {
            background: #e74c3c;
            color: white;
        }
        
        .badge-python {
            background: #3776ab;
            color: white;
        }
        
        .badge-streamlit {
            background: #ff6b6b;
            color: white;
        }
        
        .badge-ai {
            background: #9b59b6;
            color: white;
        }
        
        .architecture-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .agent-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .agent-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .agent-card h4 {
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.3em;
        }
        
        .feature-list {
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
            position: relative;
            padding-left: 25px;
        }
        
        .feature-list li:before {
            content: "✓";
            color: #27ae60;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        
        .tech-item {
            background: #34495e;
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #f39c12;
        }
        
        .info-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }
        
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }
        
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }
        
        .installation-steps {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .installation-steps ol {
            margin: 0;
            padding-left: 20px;
        }
        
        .installation-steps li {
            margin: 10px 0;
            padding: 5px 0;
        }
        
        .author-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 40px 0;
            text-align: center;
        }
        
        .author-section h3 {
            color: white;
            margin-top: 0;
        }
        
        .footer {
            text-align: center;
            color: #7f8c8d;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Multi-Agentic Health Assistant</h1>
        <p class="subtitle">A comprehensive wellness platform powered by AI agents for personalized health management</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <span class="badge badge-license">MIT License</span>
            <span class="badge badge-python">Python 3.8+</span>
            <span class="badge badge-streamlit">Streamlit</span>
            <span class="badge badge-ai">LLaMA 3.1</span>
        </div>
        
        <h2>📋 Overview</h2>
        <p>The Multi-Agentic Health Assistant is an innovative wellness platform that combines the power of multiple Large Language Models (LLMs) and vision models to provide personalized support for physical and mental well-being. The system integrates three specialized AI agents that work together to deliver comprehensive health management through diet tracking, exercise planning, and mental health support.</p>
        
        <h2>🏗️ System Architecture</h2>
        <p>The platform utilizes a multi-agent architecture with three specialized LLM agents, each designed for specific health domains:</p>
        
        <div class="architecture-grid">
            <div class="agent-card">
                <h4>🧠 Mental Health Agent</h4>
                <p><strong>Knowledge-based system</strong> for emotional support and mental wellness.</p>
                <ul class="feature-list">
                    <li>Daily check-ins and emotional support</li>
                    <li>Guided journaling and motivational prompts</li>
                    <li>Sentiment analysis and emotion classification</li>
                    <li>Secure conversation memory with flagging system</li>
                    <li>Long-term interaction tracking</li>
                </ul>
            </div>
            
            <div class="agent-card">
                <h4>🥗 Diet Agent</h4>
                <p><strong>Vision-enabled system</strong> for nutrition analysis and meal planning.</p>
                <ul class="feature-list">
                    <li>Meal planning and nutritional suggestions</li>
                    <li>Vision-based analysis of food photos</li>
                    <li>Nutrient breakdown and diet goal comparison</li>
                    <li>Dietary preference accommodation</li>
                    <li>Calorie and macro tracking</li>
                </ul>
            </div>
            
            <div class="agent-card">
                <h4>💪 Exercise Agent</h4>
                <p><strong>Database-driven system</strong> for fitness planning and tracking.</p>
                <ul class="feature-list">
                    <li>Personalized workout routine generation</li>
                    <li>Workout completion and calorie tracking</li>
                    <li>Weekly difficulty and goal adjustments</li>
                    <li>Performance data logging</li>
                    <li>Progress monitoring and analytics</li>
                </ul>
            </div>
        </div>
        
        <h2>🌟 Key Features</h2>
        <ul class="feature-list">
            <li><strong>Unified Web Interface:</strong> Streamlit-based frontend with intuitive navigation</li>
            <li><strong>Multi-Modal AI:</strong> Integration of text and vision models for comprehensive analysis</li>
            <li><strong>Personalized Recommendations:</strong> Tailored advice based on individual profiles and goals</li>
            <li><strong>Persistent Memory:</strong> Secure storage of user interactions and progress</li>
            <li><strong>Real-time Analysis:</strong> Instant feedback on meals, workouts, and mental health</li>
            <li><strong>Privacy-Focused:</strong> Secure data handling with user control over information</li>
        </ul>
        
        <h2>🔧 Tech Stack</h2>
        <div class="tech-stack">
            <span class="tech-item">LLaMA 3.1 8B (Text)</span>
            <span class="tech-item">LLaMA 3.2 11B Vision</span>
            <span class="tech-item">Streamlit</span>
            <span class="tech-item">SQLite/PostgreSQL</span>
            <span class="tech-item">Together.ai API</span>
            <span class="tech-item">Python 3.8+</span>
        </div>
        
        <h2>🚀 Getting Started</h2>
        
        <h3>Prerequisites</h3>
        <ul>
            <li>Python 3.8 or higher</li>
            <li>Together.ai API key (get $1 free credit at <a href="https://www.together.ai/" target="_blank">together.ai</a>)</li>
            <li>Basic understanding of health and wellness concepts</li>
        </ul>
        
        <div class="installation-steps">
            <h3>Installation</h3>
            <ol>
                <li><strong>Clone the repository:</strong>
                    <pre>git clone https://github.com/yourusername/multi-agentic-health-assistant.git
cd multi-agentic-health-assistant</pre>
                </li>
                <li><strong>Install dependencies:</strong>
                    <pre>pip install -r requirements.txt</pre>
                </li>
                <li><strong>Set up your API key:</strong>
                    <pre>export TOGETHER_API_KEY="your-api-key-here"</pre>
                </li>
                <li><strong>Initialize the database:</strong>
                    <pre>python setup_db.py</pre>
                </li>
                <li><strong>Run the application:</strong>
                    <pre>streamlit run app.py</pre>
                </li>
            </ol>
        </div>
        
        <div class="info-box">
            <strong>💡 Pro Tip:</strong> The $1 credit from Together.ai should be sufficient for testing and initial development. The system is designed to be cost-effective while maintaining high performance.
        </div>
        
        <h2>📱 User Interface</h2>
        <p>The web interface includes four main sections:</p>
        <ul>
            <li><strong>Dashboard:</strong> Overview of health metrics and daily progress</li>
            <li><strong>Mental Health:</strong> Chat interface with memory toggle for session continuity</li>
            <li><strong>Diet Tracker:</strong> Photo upload and analysis with nutritional breakdowns</li>
            <li><strong>Exercise Plan:</strong> Workout logging and routine management</li>
        </ul>
        
        <h2>🔮 Advanced Features</h2>
        
        <h3>Token and History Management</h3>
        <ul class="feature-list">
            <li>Rolling window context management for each LLM</li>
            <li>Automatic summarization of older conversations</li>
            <li>Long-term memory specifically for mental health continuity</li>
        </ul>
        
        <h3>Audio Integration (Optional)</h3>
        <ul class="feature-list">
            <li>Voice communication with AI agents</li>
            <li>Real-time transcription and response</li>
            <li>Hands-free interaction capability</li>
        </ul>
        
        <h2>🤝 Contributing</h2>
        <p>We welcome contributions! Please follow these steps:</p>
        <ol>
            <li>Fork the repository</li>
            <li>Create a feature branch (<code>git checkout -b feature/amazing-feature</code>)</li>
            <li>Commit your changes (<code>git commit -m 'Add amazing feature'</code>)</li>
            <li>Push to the branch (<code>git push origin feature/amazing-feature</code>)</li>
            <li>Open a Pull Request</li>
        </ol>
        
        <div class="warning-box">
            <strong>⚠️ Important:</strong> This system is designed for wellness support and should not replace professional medical advice. Always consult healthcare professionals for serious health concerns.
        </div>
        
        <h2>📄 License</h2>
        <p>This project is licensed under the MIT License. This means you are free to use, modify, and distribute the code, but the original ownership and attribution must be maintained. See the <code>LICENSE</code> file for details.</p>
        
        <h2>🔍 Future Enhancements</h2>
        <ul class="feature-list">
            <li>Integration with wearable devices</li>
            <li>Advanced analytics and reporting</li>
            <li>Social features for community support</li>
            <li>Mobile app development</li>
            <li>Healthcare provider integration</li>
        </ul>
        
        <div class="author-section">
            <h3>👨‍💻 Project Maintainer</h3>
            <p>This project is maintained and owned by <strong>[Your Name]</strong></p>
            <p>For questions, suggestions, or collaboration opportunities, feel free to reach out!</p>
        </div>
        
        <div class="footer">
            <p>Built with ❤️ for better health and wellness | © 2025 Multi-Agentic Health Assistant</p>
        </div>
    </div>
</body>
</html>
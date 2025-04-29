# Mental Health Chatbot

A mental health chatbot powered by Mistral AI through Ollama, with a Flask backend and a web interface.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [MacOS Installation](#macos-installation)
  - [Windows Installation](#windows-installation)
- [Setting Up the Project](#setting-up-the-project)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- Web-based mental health chatbot interface
- Powered by Mistral AI model via Ollama
- Flask backend API
- Cross-platform compatibility (MacOS and Windows)
- System status checks for Ollama installation

## Prerequisites

- Python 3.6+
- pip (Python package installer)
- Ollama (for running the Mistral model)
- Web browser

## Installation

### MacOS Installation

1. **Install Python (if not already installed)**:
   ```
   brew install python
   ```

2. **Install Ollama**:
   ```
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. **Start Ollama service**:
   Ollama should start automatically after installation. If it doesn't, you can start it manually:
   ```
   ollama serve
   ```

4. **Pull the Mistral model**:
   ```
   ollama pull mistral
   ```

### Windows Installation

1. **Install Python**:
   Download and install Python from the [official website](https://www.python.org/downloads/windows/).

2. **Install Ollama**:
   - Download the Windows installer from [Ollama's GitHub releases page](https://github.com/ollama/ollama/releases)
   - Run the installer and follow the on-screen instructions
   - After installation, Ollama will run as a system service

3. **Pull the Mistral model**:
   - Open Command Prompt and run:
   ```
   ollama pull mistral
   ```

## Setting Up the Project

1. **Clone this repository**:
   ```
   git clone <repository-url>
   cd mental-health-chatbot
   ```

2. **Create a virtual environment (recommended)**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On MacOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. **Install required Python packages**:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. **Ensure Ollama is running**:
   - Check status with: `ollama ps`
   - If not running, start with: `ollama serve`
   - Verify the Mistral model is downloaded: `ollama list`
   - If Mistral is not listed, download it with: `ollama pull mistral`

2. **Configure environment variables (optional)**:
   - Set the Flask port if needed: 
     - On MacOS/Linux: `export FLASK_PORT=5000`
     - On Windows: `set FLASK_PORT=5000`
   - Note: The default port is 5000, which matches the frontend configuration

3. **Start the Flask server**:
   ```
   python api.py
   ```
   
   You should see output similar to:
   ```
   Server starting on http://localhost:5000
   CORS enabled for origins: http://localhost:5000, http://localhost:5001
   ```

4. **Access the application**:
   - Backend API is available at: `http://localhost:5000`
   - Frontend interface can be accessed at: `http://localhost:5000`
   - To access from another device on the same network, use your computer's IP address instead of localhost

5. **Troubleshooting CORS issues**:
   - If experiencing CORS errors, verify:
     - You're accessing the site from one of the allowed origins (localhost:5000 or localhost:5001)
     - Both frontend and backend are running
   - For development, you can modify the CORS configuration in api.py:
     ```python
     CORS(app, origins=["your-frontend-url"], supports_credentials=True)
     ```

6. **Test the API directly**:
   - Status endpoint: `http://localhost:5000/api/status`
   - Resources endpoint: `http://localhost:5000/api/resources`
   - Chat endpoint (POST): 
     ```
     curl -X POST http://localhost:5000/api/chat \
       -H "Content-Type: application/json" \
       -d '{"message":"How can I manage stress?"}'
     ```

## API Endpoints

- **GET /api/status**: Check if Ollama is installed and running
- **POST /api/chat**: Send a message to the chatbot
  - Request body: `{"message": "Your message here"}`
  - Response: `{"response": "AI response here"}`

## Troubleshooting

- **Ollama not found**: Ensure Ollama is installed and in your system PATH
- **Connection refused**: Make sure Ollama service is running with `ollama serve`
- **CORS issues**: The API is configured to allow requests from localhost:5000 and localhost:5001. If you're hosting the frontend elsewhere, update the CORS settings in api.py

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Tailoring the LLM for Mental Wellness

To optimize the chatbot specifically for mental health support and wellness applications, consider the following strategies:

### Selecting the Appropriate Model

1. **Using specialized Mistral models**:
   ```
   # Pull a more capable model version
   ollama pull mistral:7b-instruct
   
   # Update the model in api.py
   # Change: ['ollama', 'run', 'mistral', message]
   # To:     ['ollama', 'run', 'mistral:7b-instruct', message]
   ```

2. **Consider specialized health models** if available through Ollama.

### System Prompts and Context

Add system prompts to guide the model's behavior by modifying the chat endpoint in `api.py`:

```python
# Example of using system prompt with Ollama
result = subprocess.run(
    ['ollama', 'run', 'mistral', 
     f"<system>You are a supportive mental wellness assistant. Provide empathetic, 
     non-judgmental responses. Never diagnose medical conditions or replace professional 
     mental healthcare. Always suggest consulting with a qualified professional for 
     serious concerns.</system>\n\n{message}"],
    capture_output=True,
    text=True,
    check=True
)
```

### Safety Considerations

1. **Implement response filtering** to identify and handle potentially harmful content:
   - Check for crisis indicators and provide appropriate resources
   - Filter out responses that could provide harmful advice

2. **Add disclaimers** to the chat interface indicating:
   - The chatbot is AI-based and not a replacement for professional help
   - Emergency resources for crisis situations
   - Privacy information regarding the conversation

### Content Guidelines

Create a set of mental wellness prompt templates to guide conversations in a therapeutic direction:

- **Wellness check-ins**: "How are you feeling today? Would you like to talk about it?"
- **Coping strategies**: "What are some techniques that have helped you manage stress in the past?"
- **Gratitude practices**: "Can you share something positive that happened recently?"
- **Mindfulness guidance**: "Let's try a brief mindfulness exercise together..."

### Continuous Improvement

1. **User feedback collection**: Implement a feedback system for responses
2. **Review conversations** (with appropriate privacy measures) to identify areas for improvement
3. **Keep a list of trigger topics** that should be handled with special care

### Responsible Deployment

Always include prominent disclaimers about the limitations of AI-based mental health support, and provide immediate access to crisis resources:

- National Suicide Prevention Lifeline: 988 or 1-800-273-8255
- Crisis Text Line: Text HOME to 741741

By implementing these strategies, the mental wellness chatbot can provide more appropriate, supportive, and responsible assistance while clearly acknowledging its limitations.

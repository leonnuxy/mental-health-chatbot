from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import socket
import os
import re
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__, static_folder='src')

# Fix CORS configuration - simplify and make it consistent
# Remove the specific resource configuration and use a global setting
CORS(app, origins=["http://localhost:5000", "http://localhost:5001", 
                  "http://127.0.0.1:5000", "http://127.0.0.1:5001"], 
     supports_credentials=True)

# Remove the after_request decorator as it conflicts with Flask-CORS
# and causes the Access-Control-Allow-Origin: * to override specific origins
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
#     return response

# Mental health specific configuration
MENTAL_HEALTH_SYSTEM_PROMPT = """You are a supportive mental wellness assistant designed to provide empathetic, 
non-judgmental responses. Your role is to listen, offer emotional support, and suggest healthy coping strategies.

Important guidelines to follow:
1. Never diagnose medical or psychological conditions
2. Do not provide medical advice or replace professional mental healthcare
3. Always validate the user's feelings and experiences
4. Encourage seeking professional help for serious concerns
5. Respond with empathy, warmth, and without judgment
6. Focus on evidence-based wellness practices like mindfulness, gratitude, and self-care
7. Prioritize user safety above all else

Remember that you are not a therapist, psychiatrist, or counselor. You are a supportive tool that complements, 
but does not replace, professional mental healthcare."""

# Crisis keywords that may indicate someone needs immediate help
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life", "harm myself", 
    "self-harm", "hurt myself", "cut myself", "don't want to live",
    "no reason to live", "better off dead"
]

# Emergency resources to provide during crisis detection
EMERGENCY_RESOURCES = """
If you're experiencing a mental health emergency or having thoughts of harming yourself:

- National Suicide Prevention Lifeline: Call or text 988 or call 1-800-273-8255
- Crisis Text Line: Text HOME to 741741
- Emergency Services: Call 911 (US) or your local emergency number
- Go to your nearest emergency room

Please reach out for help - trained professionals are available 24/7 to support you.
"""

def check_ollama_installed():
    """Check if Ollama is installed and available in the system PATH."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_ollama_running(host='localhost', port=11434):
    """Check if the Ollama service is running by attempting to connect to its default port."""
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except (OSError, ConnectionRefusedError):
        return False

@app.route('/api/status', methods=['GET'])
def check_status():
    """API endpoint to check if Ollama is installed and running."""
    installed = check_ollama_installed()
    running = is_ollama_running() if installed else False
    
    return jsonify({
        'installed': installed,
        'running': running
    })

def detect_crisis_language(message):
    """Detect potential crisis language in user messages."""
    message_lower = message.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            logger.warning(f"Crisis keyword detected: {keyword}")
            return True
    return False

def sanitize_user_input(message):
    """Basic sanitization and safety check for user input."""
    # Remove any potential code execution or prompt injection attempts
    message = re.sub(r'<.*?>', '', message)  # Remove HTML/XML tags
    message = re.sub(r'```.*?```', '[code block removed]', message, flags=re.DOTALL)  # Remove code blocks
    return message

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint to chat with the Ollama model tailored for mental wellness."""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Log incoming request (without PII)
    logger.info(f"Received chat request: {len(message)} chars")
    
    # Sanitize user input
    message = sanitize_user_input(message)
    
    # Check for crisis language
    if detect_crisis_language(message):
        crisis_response = {
            'response': f"I notice your message contains concerning language. Your wellbeing is important, and I want to make sure you're safe. {EMERGENCY_RESOURCES}\n\nWould you like to talk about what you're going through? I'm here to listen.",
            'crisis_detected': True
        }
        return jsonify(crisis_response)
    
    try:
        # Prepare the prompt with mental health system context
        full_prompt = f"<system>{MENTAL_HEALTH_SYSTEM_PROMPT}</system>\n\n{message}"
        
        # Connect to the already running Ollama instance with mental health context
        result = subprocess.run(
            ['ollama', 'run', 'mistral', full_prompt],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Process the response
        response = result.stdout.strip()
        
        # Log response length for monitoring
        logger.info(f"Generated response: {len(response)} chars")
        
        return jsonify({'response': response})
    except subprocess.CalledProcessError as e:
        logger.error(f"Error communicating with Ollama: {str(e)}")
        return jsonify({
            'error': str(e), 
            'response': "I'm having trouble responding right now. If you're experiencing a crisis, please use the emergency resources listed on this site or call 988 for immediate support."
        }), 500

@app.route('/api/resources', methods=['GET'])
def mental_health_resources():
    """API endpoint to provide mental health resources."""
    resources = {
        "crisis": {
            "suicide_prevention_lifeline": {
                "name": "988 Suicide & Crisis Lifeline",
                "phone": "988",
                "url": "https://988lifeline.org/"
            },
            "crisis_text_line": {
                "name": "Crisis Text Line",
                "text": "HOME to 741741",
                "url": "https://www.crisistextline.org/"
            }
        },
        "general_support": {
            "nami": {
                "name": "National Alliance on Mental Illness (NAMI)",
                "phone": "1-800-950-6264",
                "url": "https://www.nami.org/"
            },
            "samhsa": {
                "name": "Substance Abuse and Mental Health Services Administration (SAMHSA)",
                "phone": "1-800-662-4357",
                "url": "https://www.samhsa.gov/"
            }
        },
        "self_help": {
            "mindfulness_apps": ["Headspace", "Calm", "Insight Timer"],
            "wellness_techniques": ["Deep breathing", "Progressive muscle relaxation", "Gratitude journaling"]
        }
    }
    return jsonify(resources)

# Serve the static files (HTML, CSS, JS)
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Get port from environment variable or default to 5000 to match client expectations
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Print information about the running server
    print(f"Server starting on http://localhost:{port}")
    print(f"CORS enabled for origins: http://localhost:5000, http://localhost:5001")
    
    # Run the Flask application
    app.run(debug=True, port=port, host='0.0.0.0')
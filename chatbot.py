import socket
import subprocess

def check_ollama_installed():
    """Check if Ollama is installed and available in the system PATH."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, check=True)
        print("Ollama is installed.")
        return True
    except subprocess.CalledProcessError as e:
        return False
    except FileNotFoundError:
        return False

def get_ai_response(prompt):
    """Get a response from the Mistral model using Ollama."""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Sorry, I couldn't generate a response."

def is_ollama_running(host='localhost', port=11434):
    """Check if the Ollama service is running by attempting to connect to its default port."""
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except (OSError, ConnectionRefusedError):
        return False

def start_ollama_service():
    """Start the Ollama service if it's not running."""
    try:
        subprocess.Popen(['ollama', 'serve'])
        print("Starting Ollama service...")
        return True
    except Exception:
        return False

def main():
    """Main function to run the AI chatbot."""
    if not check_ollama_installed():
        print("Ollama is not installed. Please install it to use this chatbot.")
        return
    if not is_ollama_running():
        start_ollama_service()
        import time
        time.sleep(2)  # Give the service a moment to start
        if not is_ollama_running():
            print("Ollama service could not be started.")
            return
    print("Welcome to the AI Chatbot. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        response = get_ai_response(user_input)
        print(f"AI: {response}")

if __name__ == "__main__":
    main()
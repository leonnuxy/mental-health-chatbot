import subprocess

def check_ollama_installed():
    """Check if Ollama is installed and available in the system PATH."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, check=True)
        print(f"Ollama is installed. Version: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print("Ollama is not installed or not found in PATH.")
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
    except subprocess.CalledProcessError as e:
        print(f"Error generating response: {e.stderr.strip()}")
        return "Sorry, I couldn't generate a response."

def main():
    """Main function to run the AI chatbot."""
    if not check_ollama_installed():
        print("Ollama is not installed. Please install it to use this chatbot.")
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
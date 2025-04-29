#!/usr/bin/env python3
import subprocess
import webbrowser
import time
import os
import sys
import socket
import psutil

def check_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_ollama_running():
    """Check if Ollama is running using process name and port check"""
    # First check port 11434 which is Ollama's default port
    if check_port_in_use(11434):
        return True
        
    # As a backup, check running processes
    for proc in psutil.process_iter(['name']):
        try:
            if proc.name().lower() == 'ollama':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def find_available_port(start_port=5000, max_port=5100):
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port):
        if not check_port_in_use(port):
            return port
    return None

def main():
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("Ollama is not running. Starting Ollama...")
        try:
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Waiting for Ollama to start...")
            time.sleep(2)
            if not check_ollama_running():
                print("Error: Failed to start Ollama. Please start it manually with 'ollama serve'")
                return
        except FileNotFoundError:
            print("Error: Ollama is not installed. Please install it first.")
            return
    else:
        print("Ollama is already running on port 11434.")
    
    # Find an available port for the API server
    api_port = find_available_port(5000)
    if not api_port:
        print("Error: Could not find an available port for the API server.")
        return
    
    print(f"Starting Flask API server on port {api_port}...")
    
    # Set the port as an environment variable for Flask
    env = os.environ.copy()
    env["FLASK_PORT"] = str(api_port)
    
    # Start Flask API
    api_process = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, 'api.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    time.sleep(1)  # Give the API server time to start
    
    # Open the web browser
    print(f"Opening application in web browser at http://localhost:{api_port}")
    webbrowser.open(f'http://localhost:{api_port}')
    
    print("Mental Health Chatbot is now running!")
    print("Press Ctrl+C to shut down the server.")
    
    try:
        # Keep the script running until keyboard interrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        api_process.terminate()
        print("Server stopped. Goodbye!")

if __name__ == "__main__":
    main()

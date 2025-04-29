document.addEventListener('DOMContentLoaded', function() {
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const aiStatusIndicator = document.getElementById('ai-status-indicator');
    const aiStatusText = document.getElementById('ai-status-text');

    // API URL configuration - Try multiple possible ports
    const API_PORTS = [5000, 5001];
    let API_BASE_URL = null;

    // Function to find the working API endpoint
    async function findWorkingApiEndpoint() {
        for (const port of API_PORTS) {
            const url = `http://localhost:${port}`;
            try {
                const response = await fetch(`${url}/api/status`, {
                    method: 'GET',
                    mode: 'cors',
                    headers: {
                        'Accept': 'application/json',
                    }
                });
                
                if (response.ok) {
                    console.log(`API found at ${url}`);
                    return url;
                }
            } catch (error) {
                console.log(`API not available at ${url}`);
            }
        }
        return null;
    }

    // Initialize the API connection
    async function initializeApiConnection() {
        API_BASE_URL = await findWorkingApiEndpoint();
        
        if (API_BASE_URL) {
            console.log(`Connected to API at ${API_BASE_URL}`);
            checkOllamaStatus();
        } else {
            setStatusError("API server not found");
            console.error("Could not connect to API on any port");
            
            // Add an error message to the chat
            addMessage("Could not connect to the AI service. Please make sure the server is running.", false);
        }
    }

    // Check if Ollama is running
    async function checkOllamaStatus() {
        if (!API_BASE_URL) {
            setStatusError("API connection not established");
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/status`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.running) {
                setStatusOnline();
            } else {
                setStatusOffline("Ollama is installed but not running");
            }
        } catch (error) {
            setStatusError("API server unreachable");
            console.error('Error checking Ollama status:', error);
        }
    }

    // Set status to online
    function setStatusOnline() {
        aiStatusIndicator.className = 'status-indicator status-online pulse-dot';
        aiStatusText.textContent = 'AI Assistant (Online)';
        chatbotSend.disabled = false;
        chatbotInput.disabled = false;
        chatbotInput.placeholder = "Message Mental Wellness...";
    }

    // Set status to offline
    function setStatusOffline(reason = "AI Assistant is offline") {
        aiStatusIndicator.className = 'status-indicator status-offline';
        aiStatusText.textContent = 'AI Assistant (Offline)';
        chatbotSend.disabled = true;
        chatbotInput.disabled = true;
        chatbotInput.placeholder = reason;
    }

    // Set status to error
    function setStatusError(reason = "Error connecting to AI") {
        aiStatusIndicator.className = 'status-indicator status-error';
        aiStatusText.textContent = 'AI Assistant (Error)';
        chatbotSend.disabled = true;
        chatbotInput.disabled = true;
        chatbotInput.placeholder = reason;
    }

    // Function to add a new message to the chat
    function addMessage(content, isUser) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message-wrapper ${isUser ? 'user-message' : 'ai-message'}`;

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';

        const messageAvatar = document.createElement('div');
        messageAvatar.className = 'message-avatar';

        // Create avatar SVG based on who's sending the message
        let avatarSvg;
        if (isUser) {
            avatarSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>`;
        } else {
            avatarSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>`;
        }
        
        messageAvatar.innerHTML = avatarSvg;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${content}</p>`;

        messageBubble.appendChild(messageAvatar);
        messageBubble.appendChild(messageContent);
        messageWrapper.appendChild(messageBubble);
        chatbotMessages.appendChild(messageWrapper);

        // Scroll to the bottom of the chat
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Function to hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.classList.add('hidden');
    }

    // Function to handle sending a message
    async function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message && API_BASE_URL) {
            // Add user message
            addMessage(message, true);
            chatbotInput.value = '';
            
            // Reset input height
            chatbotInput.style.height = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                // Send message to API
                const response = await fetch(`${API_BASE_URL}/api/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                hideTypingIndicator();
                addMessage(data.response, false);
            } catch (error) {
                hideTypingIndicator();
                console.error('Error:', error);
                addMessage("I'm sorry, I couldn't process your request at the moment.", false);
                // Check ollama status again in case it went offline
                checkOllamaStatus();
            }
        }
    }

    // Event listeners
    chatbotSend.addEventListener('click', sendMessage);
    
    chatbotInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!chatbotSend.disabled) {
                sendMessage();
            }
        }
    });
    
    // Enable send button when input has text
    chatbotInput.addEventListener('input', function() {
        // Auto-resize textarea
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        // Enable/disable send button based on content
        if (this.value.trim() !== '') {
            chatbotSend.classList.add('active');
        } else {
            chatbotSend.classList.remove('active');
        }
    });

    // Initialize API connection and check status
    initializeApiConnection();
    
    // Check Ollama status periodically
    setInterval(checkOllamaStatus, 30000);
});

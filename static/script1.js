document.addEventListener('DOMContentLoaded', function() {
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const queryCount = document.getElementById('queryCount');
    
    // Initialize query count (in a real app, this would come from a server)
    let count = localStorage.getItem('queryCount') || 0;
    queryCount.textContent = count;
    
    // Add event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Add click handlers for popular topics
    const topicTags = document.querySelectorAll('.topic-tag');
    topicTags.forEach(tag => {
        tag.addEventListener('click', function() {
            userInput.value = this.textContent;
            userInput.focus();
        });
    });
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Increment query count
        count++;
        queryCount.textContent = count;
        localStorage.setItem('queryCount', count);
        
        // Send message to server and get response - UPDATED ENDPOINT
        fetch('/api/chat', {  // CHANGED from '/ask' to '/api/chat'
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            if (data.error) {
                addMessage("Sorry, I'm having trouble answering right now. Please try again later.", 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(error => {
            removeTypingIndicator();
            console.error('Chat error:', error);
            
            // Provide more specific error messages
            if (error.message.includes('401') || error.message.includes('403')) {
                addMessage("Please login to use the AI Health Advisor.", 'bot');
            } else if (error.message.includes('500')) {
                addMessage("Sorry, the AI service is currently unavailable. Please try again later.", 'bot');
            } else {
                addMessage("Sorry, there was an error processing your request. Please check your connection and try again.", 'bot');
            }
        });
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        // Format the bot's response for better readability
        let formattedText = text;
        if (sender === 'bot') {
            // Add line breaks for better formatting
            formattedText = text.replace(/\n/g, '<br>');
            
            // Add bullet points for lists
            formattedText = formattedText.replace(/\•/g, '<br>• ');
            formattedText = formattedText.replace(/(\d+\.)/g, '<br>$1');
        }
        
        content.innerHTML = `<p>${formattedText}</p>`;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatBox.appendChild(messageDiv);
        
        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Add CSS for typing indicator
    if (!document.getElementById('chat-styles')) {
        const style = document.createElement('style');
        style.id = 'chat-styles';
        style.textContent = `
            .typing-indicator {
                display: flex;
                align-items: center;
                margin: 15px 0;
                animation: fadeIn 0.3s ease;
            }
            
            .typing-dots {
                display: flex;
                gap: 4px;
                padding: 10px 15px;
                background: #f0f0f0;
                border-radius: 18px;
                border-top-left-radius: 5px;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: #888;
                border-radius: 50%;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-dot:nth-child(1) {
                animation-delay: -0.32s;
            }
            
            .typing-dot:nth-child(2) {
                animation-delay: -0.16s;
            }
            
            @keyframes typing {
                0%, 80%, 100% {
                    transform: scale(0.8);
                    opacity: 0.5;
                }
                40% {
                    transform: scale(1);
                    opacity: 1;
                }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Auto-focus on input when page loads
    userInput.focus();
});
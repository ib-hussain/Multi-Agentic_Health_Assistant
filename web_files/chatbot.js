document.addEventListener("DOMContentLoaded", function() {
            const messageForm = document.getElementById('message-form');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const chatMessages = document.getElementById('chat-messages');
            let isTyping = false;

            messageForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const message = userInput.value.trim();
                
                if (message && !isTyping) {
                    // Disable input and button
                    setInputState(false);
                    isTyping = true;
                    
                    // Add user message to chat
                    addMessage(message, 'user-message');
                    userInput.value = '';
                    
                    // Show typing indicator
                    const typingIndicator = addTypingIndicator();
                    
                    // Simulate bot response after a delay
                    setTimeout(() => {
                        // Remove typing indicator
                        typingIndicator.remove();
                        
                        // Add bot response
                        addMessage("I'm your virtual health assistant. How can I help you today?", 'bot-message');
                        
                        // Re-enable input and button
                        setInputState(true);
                        isTyping = false;
                    }, 2000); // 2 second delay to simulate processing
                }
            });

            function setInputState(enabled) {
                userInput.disabled = !enabled;
                sendBtn.disabled = !enabled;
                if (enabled) {
                    userInput.placeholder = "Type your message here...";
                } else {
                    userInput.placeholder = "Please wait for response...";
                }
            }

            function addMessage(text, className) {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', className);
                messageElement.textContent = text;
                chatMessages.appendChild(messageElement);
                
                // Smooth scroll to bottom of page with extra offset
                setTimeout(() => {
                    window.scrollTo({
                        top: document.body.scrollHeight + 100,
                        behavior: 'smooth'
                    });
                }, 150);
            }

            function addTypingIndicator() {
                const typingElement = document.createElement('div');
                typingElement.classList.add('typing-indicator');
                typingElement.innerHTML = `
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                `;
                chatMessages.appendChild(typingElement);
                
                // Smooth scroll to bottom of page with extra offset
                setTimeout(() => {
                    window.scrollTo({
                        top: document.body.scrollHeight + 100,
                        behavior: 'smooth'
                    });
                }, 150);
                
                return typingElement;
            }
        });
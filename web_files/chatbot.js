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
                        
                        // Add bot response with markdown formatting
                        addMessage("**Calories:** \n* Apple - 95 calories\n* Banana * - 105 calories\n *Orange* - 62 calories\n\n*This is sample formatted response*", 'bot-message');
                        
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
                
                // Parse markdown formatting for bot messages
                if (className === 'bot-message') {
                    messageElement.innerHTML = parseMarkdown(text);
                } else {
                    messageElement.textContent = text;
                }
                
                chatMessages.appendChild(messageElement);
                
                // Smooth scroll to bottom of page with extra offset
                setTimeout(() => {
                    window.scrollTo({
                        top: document.body.scrollHeight + 100,
                        behavior: 'smooth'
                    });
                }, 150);
            }

            function parseMarkdown(text) {
                // Convert markdown to HTML
                let html = text
                    // Bold text: **text** or __text__
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/__(.*?)__/g, '<strong>$1</strong>')
                    
                    // Italic text: *text* or _text_
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/_(.*?)_/g, '<em>$1</em>')
                    
                    // Code: `code`
                    .replace(/`(.*?)`/g, '<code>$1</code>')
                    
                    // Line breaks
                    .replace(/\n\n/g, '</p><p>')
                    .replace(/\n/g, '<br>');

                // Handle lists
                html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
                html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
                
                // Handle numbered lists
                html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
                html = html.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');

                // Wrap in paragraph if not already wrapped
                if (!html.startsWith('<')) {
                    html = '<p>' + html + '</p>';
                } else if (html.includes('<br>') && !html.includes('<p>')) {
                    html = '<p>' + html + '</p>';
                }

                return html;
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
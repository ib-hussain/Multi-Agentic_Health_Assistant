document.addEventListener("DOMContentLoaded", function() {
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        
        if (message) {
            // Add user message to chat
            addMessage(message, 'user-message');
            userInput.value = '';
            
            // Simulate bot response after a short delay
            setTimeout(() => {
                addMessage("I'm your virtual health assistant. How can I help you today?", 'bot-message');
            }, 1000);
        }
    });

    function addMessage(text, className) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', className);
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
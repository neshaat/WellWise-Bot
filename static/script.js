document.addEventListener('DOMContentLoaded', function () {
    const chatHistory = document.getElementById('chat-history');
    const chatForm = document.getElementById('chat-form');

    // Initial greeting from bot
    appendMessage('WellWise Bot: Greetings! How may I assist you today?', true);

    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const userInput = document.getElementById('user-input').value;

        // Display user input
        appendMessage('User: ' + userInput);

        // Send user input to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ 'user_input': userInput }),
        })
        .then(response => response.json())
        .then(data => {
            // Display bot response
            appendMessage(data.bot_response, true);

            // If asking for advice, display additional message
            if (data.asking_for_advice) {
                getPrecaution(data.prompt);
            }
        })
        .catch(error => console.error('Error:', error));

        // Clear user input field
        document.getElementById('user-input').value = '';
    });

    function appendMessage(message, isBotMessage = false) {
        const p = document.createElement('p');
        p.textContent = message;
        p.classList.add('chat-message');
        if (isBotMessage) {
            p.classList.add('chat-message-bot');
        }
        chatHistory.appendChild(p);
    }

    function getPrecaution(prompt) {
        // Send prompt to server to get precaution advice
        fetch('/get_precaution', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'prompt': prompt }),
        })
        .then(response => response.json())
        .then(data => {
            // Display precaution advice
            appendMessage('WellWise Bot: ' + data.precaution, true);
        })
        .catch(error => console.error('Error:', error));
    }
});

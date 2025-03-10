// Creación de chat.js para la interfaz de chat

const chatJs = `document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const agentSelect = document.getElementById('agentSelect');

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        const selectedAgent = agentSelect.value;

        if (message && selectedAgent) {
            // Add user message to chat
            addMessage('user', message);

            // Send message to backend
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    agent: selectedAgent
                })
            })
            .then(response => response.json())
            .then(data => {
                // Add agent response to chat
                addMessage('agent', data.response);
                
                if (data.task_id) {
                    // Poll for task updates
                    const pollInterval = setInterval(() => {
                        fetch(\`/api/tasks/\${data.task_id}\`)
                            .then(response => response.json())
                            .then(taskData => {
                                if (taskData.status === 'completed' && taskData.result) {
                                    addMessage('agent', taskData.result);
                                    clearInterval(pollInterval);
                                } else if (taskData.status === 'failed') {
                                    addMessage('agent', 'Sorry, there was an error processing your request.');
                                    clearInterval(pollInterval);
                                }
                            })
                            .catch(error => {
                                console.error('Error polling task:', error);
                                clearInterval(pollInterval);
                            });
                    }, 2000); // Poll every 2 seconds
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('agent', 'Sorry, there was an error processing your request.');
            });

            messageInput.value = '';
        }
    });

    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = \`message \${type}-message\`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});`;

console.log("Archivo chat.js creado para la interfaz de chat.");
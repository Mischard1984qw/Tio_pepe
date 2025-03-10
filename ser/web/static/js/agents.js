// Actualización de agents.js para trabajar con los agentes especializados

const agentsJs = `document.addEventListener('DOMContentLoaded', function() {
    // Fetch agent data
    function fetchAgents() {
        fetch('/api/agents')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch agents');
                }
                return response.json();
            })
            .then(data => {
                if (data.agents && data.agents.length > 0) {
                    data.agents.forEach(agent => {
                        updateAgentCard(agent);
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching agents:', error);
            });
    }

    // Update agent card with data
    function updateAgentCard(agent) {
        // Map agent type to agent ID in the DOM
        const agentTypeMap = {
            'NLPAgent': 'nlp',
            'VisionAgent': 'vision',
            'WebAgent': 'web',
            'DataAgent': 'data',
            'CodeAgent': 'code',
            'PlanningAgent': 'planning'
        };
        
        const agentId = agentTypeMap[agent.type] || agent.id;
        const agentCard = document.getElementById(\`\${agentId}-agent\`);
        if (!agentCard) return;

        const statusIndicator = agentCard.querySelector('.status-indicator');
        const tasksProcessed = agentCard.querySelector('.agent-metrics div:first-child .metric');
        const successRate = agentCard.querySelector('.agent-metrics div:last-child .metric');

        // Update status
        statusIndicator.textContent = agent.status;
        statusIndicator.className = 'status-indicator';
        if (agent.status === 'active') {
            statusIndicator.classList.add('status-active');
        } else {
            statusIndicator.classList.add('status-inactive');
        }

        // Update metrics
        tasksProcessed.textContent = agent.tasks_processed || 0;
        successRate.textContent = \`\${agent.success_rate || 0}%\`;

        // Add click handler for agent activation/deactivation
        agentCard.addEventListener('click', function() {
            if (!agentCard.classList.contains('restricted')) {
                toggleAgentStatus(agent.id, agent.status);
            }
        });
    }

    // Toggle agent status
    function toggleAgentStatus(agentId, currentStatus) {
        const endpoint = currentStatus === 'active' ? 'deactivate' : 'activate';
        
        fetch(\`/api/agents/\${agentId}/\${endpoint}\`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(\`Failed to \${endpoint} agent\`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Refresh agent data
                fetchAgents();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Initial fetch
    fetchAgents();
    
    // Refresh data every 5 seconds
    setInterval(fetchAgents, 5000);
});`;

console.log("Archivo agents.js actualizado para trabajar con los agentes especializados.");
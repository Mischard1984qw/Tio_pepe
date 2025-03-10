const dashboardJs = `document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const activeTasksCount = document.getElementById('active-tasks-count');
    const activeAgentsCount = document.getElementById('active-agents-count');
    const systemStatus = document.getElementById('system-status');
    const activityFeed = document.getElementById('activity-feed');
    
    // Charts
    let agentPerformanceChart;
    let taskDistributionChart;

    // Initialize charts
    function initCharts() {
        // Agent Performance Chart
        const agentPerformanceCtx = document.getElementById('agentPerformanceChart').getContext('2d');
        agentPerformanceChart = new Chart(agentPerformanceCtx, {
            type: 'bar',
            data: {
                labels: ['NLP', 'Visión', 'Web', 'Datos', 'Planificación', 'Código'],
                datasets: [{
                    label: 'Tareas Completadas',
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
        
        // Task Distribution Chart
        const taskDistributionCtx = document.getElementById('taskDistributionChart').getContext('2d');
        taskDistributionChart = new Chart(taskDistributionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pendientes', 'En Ejecución', 'Completadas', 'Fallidas'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(243, 156, 18, 0.7)',
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(231, 76, 60, 0.7)'
                    ],
                    borderColor: [
                        'rgba(243, 156, 18, 1)',
                        'rgba(52, 152, 219, 1)',
                        'rgba(46, 204, 113, 1)',
                        'rgba(231, 76, 60, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Fetch dashboard metrics
    function fetchDashboardMetrics() {
        fetch('/api/dashboard/metrics')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch dashboard metrics');
                }
                return response.json();
            })
            .then(data => {
                // Update metrics
                activeTasksCount.textContent = data.active_tasks;
                activeAgentsCount.textContent = data.active_agents;
                
                // Update system status with appropriate class
                systemStatus.textContent = data.system_status === 'healthy' ? 'Saludable' : 
                                          (data.system_status === 'degraded' ? 'Degradado' : 'Error');
                systemStatus.className = 'status';
                if (data.system_status === 'healthy') {
                    systemStatus.classList.add('status-healthy');
                } else if (data.system_status === 'degraded') {
                    systemStatus.classList.add('status-warning');
                } else {
                    systemStatus.classList.add('status-error');
                }
                
                // Update charts if available
                if (data.agent_performance) {
                    updateAgentPerformanceChart(data.agent_performance);
                }
                
                if (data.task_distribution) {
                    updateTaskDistributionChart(data.task_distribution);
                }
            })
            .catch(error => {
                console.error('Error fetching dashboard metrics:', error);
                systemStatus.textContent = 'Error';
                systemStatus.className = 'status status-error';
            });
    }

    // Update Agent Performance Chart
    function updateAgentPerformanceChart(data) {
        if (!agentPerformanceChart) return;
        
        // If no real data is available, use sample data
        const performanceData = data || {
            'nlp': Math.floor(Math.random() * 10),
            'vision': Math.floor(Math.random() * 10),
            'web': Math.floor(Math.random() * 10),
            'data': Math.floor(Math.random() * 10),
            'planning': Math.floor(Math.random() * 10),
            'code': Math.floor(Math.random() * 10)
        };
        
        agentPerformanceChart.data.datasets[0].data = [
            performanceData.nlp || 0,
            performanceData.vision || 0,
            performanceData.web || 0,
            performanceData.data || 0,
            performanceData.planning || 0,
            performanceData.code || 0
        ];
        
        agentPerformanceChart.update();
    }

    // Update Task Distribution Chart
    function updateTaskDistributionChart(data) {
        if (!taskDistributionChart) return;
        
        // If no real data is available, use sample data
        const distributionData = data || {
            'pending': Math.floor(Math.random() * 5),
            'running': Math.floor(Math.random() * 5),
            'completed': Math.floor(Math.random() * 10),
            'failed': Math.floor(Math.random() * 3)
        };
        
        taskDistributionChart.data.datasets[0].data = [
            distributionData.pending || 0,
            distributionData.running || 0,
            distributionData.completed || 0,
            distributionData.failed || 0
        ];
        
        taskDistributionChart.update();
    }

    // Fetch activity feed
    function fetchActivityFeed() {
        fetch('/api/activity')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch activity feed');
                }
                return response.json();
            })
            .then(data => {
                // Clear existing activities
                activityFeed.innerHTML = '';
                
                // Add new activities
                if (data.activities && data.activities.length > 0) {
                    data.activities.forEach(activity => {
                        const activityItem = document.createElement('div');
                        activityItem.className = 'activity-item';
                        
                        // Format timestamp
                        const date = new Date(activity.timestamp * 1000);
                        const formattedTime = date.toLocaleTimeString();
                        
                        activityItem.innerHTML = \`
                            <div class="activity-time">\${formattedTime}</div>
                            <div class="activity-description">\${activity.description}</div>
                        \`;
                        
                        activityFeed.appendChild(activityItem);
                    });
                } else {
                    activityFeed.innerHTML = '<div class="no-activity">No hay actividad reciente</div>';
                }
            })
            .catch(error => {
                console.error('Error fetching activity feed:', error);
                activityFeed.innerHTML = '<div class="error-message">Error al cargar la actividad reciente</div>';
            });
    }

    // Initialize charts
    initCharts();

    // Initial fetch
    fetchDashboardMetrics();
    fetchActivityFeed();
    
    // Refresh data every 10 seconds
    setInterval(function() {
        fetchDashboardMetrics();
        fetchActivityFeed();
    }, 10000);
});`;

console.log("Archivo dashboard.js actualizado con gráficos y datos de muestra.");

// 3.2. web/static/js/agents.js
const agentsJs = `document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const agentSearch = document.getElementById('agent-search');
    const agentStatusFilter = document.getElementById('agent-status-filter');
    const agentCards = document.querySelectorAll('.agent-card');
    
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
        statusIndicator.textContent = agent.status === 'active' ? 'Activo' : 'Inactivo';
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

    // Filter agents by search term
    function filterAgentsBySearch(searchTerm) {
        agentCards.forEach(card => {
            const agentName = card.querySelector('h2').textContent.toLowerCase();
            const agentDescription = card.querySelector('.agent-description').textContent.toLowerCase();
            
            if (agentName.includes(searchTerm) || agentDescription.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // Filter agents by status
    function filterAgentsByStatus(status) {
        if (status === 'all') {
            agentCards.forEach(card => {
                card.style.display = '';
            });
            return;
        }
        
        agentCards.forEach(card => {
            const agentStatus = card.querySelector('.status-indicator').textContent.toLowerCase();
            
            if ((status === 'active' && agentStatus === 'activo') || 
                (status === 'inactive' && agentStatus === 'inactivo')) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // Add event listeners
    if (agentSearch) {
        agentSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterAgentsBySearch(searchTerm);
        });
    }
    
    if (agentStatusFilter) {
        agentStatusFilter.addEventListener('change', function() {
            filterAgentsByStatus(this.value);
        });
    }

    // Initial fetch
    fetchAgents();
    
    // Refresh data every 5 seconds
    setInterval(fetchAgents, 5000);
});`;

console.log("Archivo agents.js actualizado con funcionalidad de búsqueda y filtrado.");

// 3.3. web/static/js/tasks.js
const tasksJs = `document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tasksTable = document.getElementById('tasks-table');
    const tasksBody = document.getElementById('tasks-body');
    const newTaskBtn = document.getElementById('new-task-btn');
    const taskModal = document.getElementById('task-modal');
    const taskDetailModal = document.getElementById('task-detail-modal');
    const taskForm = document.getElementById('task-form');
    const cancelTaskBtn = document.getElementById('cancel-task');
    const closeDetailBtn = document.getElementById('close-detail');
    const taskStatusFilter = document.getElementById('task-status-filter');
    const taskAgentFilter = document.getElementById('task-agent-filter');
    const taskAgent = document.getElementById('task-agent');
    const taskType = document.getElementById('task-type');
    const taskData = document.getElementById('task-data');
    const taskDetailContent = document.getElementById('task-detail-content');

    // Task type options by agent
    const taskTypesByAgent = {
        'nlp': [
            { value: 'sentiment', label: 'Análisis de Sentimiento' },
            { value: 'generation', label: 'Generación de Texto' },
            { value: 'classification', label: 'Clasificación de Texto' }
        ],
        'vision': [
            { value: 'object_detection', label: 'Detección de Objetos' },
            { value: 'face_detection', label: 'Detección de Caras' },
            { value: 'image_classification', label: 'Clasificación de Imágenes' }
        ],
        'web': [
            { value: 'scrape_static', label: 'Scraping Estático' },
            { value: 'scrape_dynamic', label: 'Scraping Dinámico' },
            { value: 'extract_links', label: 'Extracción de Enlaces' }
        ],
        'data': [
            { value: 'analysis', label: 'Análisis de Datos' },
            { value: 'transformation', label: 'Transformación de Datos' },
            { value: 'statistics', label: 'Estadísticas' }
        ],
        'planning': [
            { value: 'create_workflow', label: 'Crear Flujo de Trabajo' },
            { value: 'add_task', label: 'Añadir Tarea' },
            { value: 'get_status', label: 'Obtener Estado' }
        ],
        'code': [
            { value: 'optimize', label: 'Optimizar Código' },
            { value: 'analyze', label: 'Analizar Código' },
            { value: 'generate', label: 'Generar Código' }
        ]
    };

    // Sample task data templates by type
    const taskDataTemplates = {
        'sentiment': {
            'nlp_type': 'sentiment',
            'text': 'Me encanta este producto, es fantástico!'
        },
        'object_detection': {
            'vision_type': 'object_detection',
            'image_path': '/path/to/image.jpg'
        },
        'scrape_static': {
            'web_type': 'scrape_static',
            'url': 'https://example.com'
        },
        'analysis': {
            'data_type': 'analysis',
            'data': [
                {'id': 1, 'value': 10},
                {'id': 2, 'value': 20},
                {'id': 3, 'value': 30}
            ]
        },
        'create_workflow': {
            'workflow_id': 'workflow_1',
            'name': 'Mi Flujo de Trabajo'
        },
        'optimize': {
            'code_type': 'optimize',
            'language': 'python',
            'code': 'def hello_world():\\n    print("Hello, World!")'
        }
    };

    // Fetch tasks
    function fetchTasks() {
        // Get filter values
        const statusFilter = taskStatusFilter.value;
        const agentFilter = taskAgentFilter.value;
        
        let url = '/api/tasks';
        const params = [];
        
        if (statusFilter !== 'all') {
            params.push(\`status=\${statusFilter}\`);
        }
        
        if (agentFilter !== 'all') {
            params.push(\`agent=\${agentFilter}\`);
        }
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch tasks');
                }
                return response.json();
            })
            .then(data => {
                // Clear existing tasks
                tasksBody.innerHTML = '';
                
                // Add tasks to table
                if (data.tasks && data.tasks.length > 0) {
                    data.tasks.forEach(task => {
                        addTaskRow(task);
                    });
                } else {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = '<td colspan="6" class="text-center">No se encontraron tareas</td>';
                    tasksBody.appendChild(emptyRow);
                }
            })
            .catch(error => {
                console.error('Error fetching tasks:', error);
                tasksBody.innerHTML = '<tr><td colspan="6" class="text-center error-message">Error al cargar las tareas</td></tr>';
            });
    }

    // Add task row to table
    function addTaskRow(task) {
        const row = document.createElement('tr');
        
        // Format date
        const date = new Date(task.created_at * 1000);
        const formattedDate = date.toLocaleString();
        
        // Translate status
        const statusMap = {
            'pending': 'Pendiente',
            'running': 'En Ejecución',
            'completed': 'Completada',
            'failed': 'Fallida'
        };
        
        const translatedStatus = statusMap[task.status] || task.status;
        
        row.innerHTML = \`
            <td>\${task.id}</td>
            <td>\${task.type}</td>
            <td>\${task.agent || '-'}</td>
            <td><span class="status-\${task.status}">\${translatedStatus}</span></td>
            <td>\${formattedDate}</td>
            <td>
                <button class="btn btn-sm view-task" data-task-id="\${task.id}">Ver</button>
            </td>
        \`;
        
        tasksBody.appendChild(row);
        
        // Add event listener to view button
        row.querySelector('.view-task').addEventListener('click', function() {
            viewTask(task.id);
        });
    }

    // View task details
    function viewTask(taskId) {
        fetch(\`/api/tasks/\${taskId}\`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch task details');
                }
                return response.json();
            })
            .then(task => {
                // Format date
                const createdDate = new Date(task.created_at * 1000);
                const formattedCreatedDate = createdDate.toLocaleString();
                
                let formattedStartDate = 'N/A';
                if (task.start_time) {
                    const startDate = new Date(task.start_time * 1000);
                    formattedStartDate = startDate.toLocaleString();
                }
                
                let formattedEndDate = 'N/A';
                if (task.end_time) {
                    const endDate = new Date(task.end_time * 1000);
                    formattedEndDate = endDate.toLocaleString();
                }
                
                // Translate status
                const statusMap = {
                    'pending': 'Pendiente',
                    'running': 'En Ejecución',
                    'completed': 'Completada',
                    'failed': 'Fallida'
                };
                
                const translatedStatus = statusMap[task.status] || task.status;
                
                // Format task data
                const taskDataFormatted = JSON.stringify(task.data, null, 2);
                
                // Format result if available
                let resultHtml = '<p>No hay resultados disponibles</p>';
                if (task.result) {
                    resultHtml = \`<pre>\${JSON.stringify(task.result, null, 2)}</pre>\`;
                }
                
                taskDetailContent.innerHTML = \`
                    <div class="task-detail-header">
                        <h3>Tarea #\${task.id}</h3>
                        <span class="status-\${task.status}">\${translatedStatus}</span>
                    </div>
                    <div class="task-detail-info">
                        <div class="detail-row">
                            <div class="detail-label">Tipo:</div>
                            <div class="detail-value">\${task.type}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Agente:</div>
                            <div class="detail-value">\${task.agent || 'N/A'}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Creada:</div>
                            <div class="detail-value">\${formattedCreatedDate}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Iniciada:</div>
                            <div class="detail-value">\${formattedStartDate}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Finalizada:</div>
                            <div class="detail-value">\${formattedEndDate}</div>
                        </div>
                    </div>
                    <div class="task-detail-section">
                        <h4>Datos de la Tarea</h4>
                        <pre>\${taskDataFormatted}</pre>
                    </div>
                    <div class="task-detail-section">
                        <h4>Resultado</h4>
                        \${resultHtml}
                    </div>
                \`;
                
                // Show the modal
                taskDetailModal.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching task details:', error);
                alert('Error al cargar los detalles de la tarea');
            });
    }

    // Update task type options based on selected agent
    function updateTaskTypeOptions() {
        const selectedAgent = taskAgent.value;
        
        // Clear current options
        taskType.innerHTML = '';
        
        // Add new options
        if (selectedAgent && taskTypesByAgent[selectedAgent]) {
            taskTypesByAgent[selectedAgent].forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                taskType.appendChild(optionElement);
            });
            
            // Update task data template
            updateTaskDataTemplate();
        } else {
            const optionElement = document.createElement('option');
            optionElement.value = '';
            optionElement.textContent = 'Selecciona un agente primero';
            taskType.appendChild(optionElement);
            
            // Clear task data
            taskData.value = '';
        }
    }

    // Update task data template based on selected type
    function updateTaskDataTemplate() {
        const selectedType = taskType.value;
        
        if (selectedType && taskDataTemplates[selectedType]) {
            taskData.value = JSON.stringify(taskDataTemplates[selectedType], null, 2);
        } else {
            // Provide a generic template
            taskData.value = '{\n  "key": "value"\n}';
        }
    }

    // Add event listeners
    if (newTaskBtn) {
        newTaskBtn.addEventListener('click', function() {
            taskModal.style.display = 'block';
        });
    }
    
    if (cancelTaskBtn) {
        cancelTaskBtn.addEventListener('click', function() {
            taskModal.style.display = 'none';
        });
    }
    
    if (closeDetailBtn) {
        closeDetailBtn.addEventListener('click', function() {
            taskDetailModal.style.display = 'none';
        });
    }
    
    if (taskForm) {
        taskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            try {
                const taskDataObj = JSON.parse(taskData.value);
                
                const newTask = {
                    agent: taskAgent.value,
                    type: taskType.value,
                    data: taskDataObj
                };
                
                fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(newTask)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to create task');
                    }
                    return response.json();
                })
                .then(data => {
                    // Close modal and refresh tasks
                    taskModal.style.display = 'none';
                    fetchTasks();
                })
                .catch(error => {
                    console.error('Error creating task:', error);
                    alert('Error al crear la tarea');
                });
            } catch (error) {
                alert('Error en el formato JSON de los datos de la tarea');
            }
        });
    }
    
    if (taskAgent) {
        taskAgent.addEventListener('change', updateTaskTypeOptions);
    }
    
    if (taskType) {
        taskType.addEventListener('change', updateTaskDataTemplate);
    }
    
    if (taskStatusFilter) {
        taskStatusFilter.addEventListener('change', fetchTasks);
    }
    
    if (taskAgentFilter) {
        taskAgentFilter.addEventListener('change', fetchTasks);
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === taskModal) {
            taskModal.style.display = 'none';
        }
        if (event.target === taskDetailModal) {
            taskDetailModal.style.display = 'none';
        }
    });

    // Initial fetch
    fetchTasks();
    
    // Initialize task type options
    if (taskAgent) {
        updateTaskTypeOptions();
    }
    
    // Refresh data every 10 seconds
    setInterval(fetchTasks, 10000);
});`;

console.log("Archivo tasks.js actualizado con plantillas de tareas y visualización detallada.");

// 3.4. web/static/js/chat.js
const chatJs = `document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const agentSelect = document.getElementById('agentSelect');
    const chatTitle = document.getElementById('chatTitle');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const exportChatBtn = document.getElementById('exportChatBtn');
    const agentInfo = document.getElementById('agentInfo');
    const chatHistory = document.getElementById('chatHistory');

    // Agent descriptions
    const agentDescriptions = {
        'nlp': {
            name: 'Agente NLP',
            description: 'Procesamiento de lenguaje natural, análisis de sentimientos, generación de texto',
            capabilities: [
                'Análisis de sentimiento de texto',
                'Generación de texto basado en prompts',
                'Clasificación de texto en categorías',
                'Extracción de entidades y conceptos clave'
            ]
        },
        'vision': {
            name: 'Agente de Visión',
            description: 'Procesamiento de imágenes, detección de objetos, clasificación',
            capabilities: [
                'Detección de objetos en imágenes',
                'Reconocimiento facial',
                'Clasificación de imágenes',
                'Análisis de escenas'
            ]
        },
        'web': {
            name: 'Agente Web',
            description: 'Búsqueda y extracción web, scraping, integración con APIs',
            capabilities: [
                'Extracción de contenido de páginas web',
                'Navegación por sitios dinámicos',
                'Extracción de enlaces y recursos',
                'Monitoreo de cambios en sitios web'
            ]
        },
        'data': {
            name: 'Agente de Datos',
            description: 'Análisis de datos, transformaciones, estadísticas',
            capabilities: [
                'Análisis estadístico de conjuntos de datos',
                'Transformación y limpieza de datos',
                'Visualización de datos',
                'Detección de anomalías'
            ]
        },
        'planning': {
            name: 'Agente de Planificación',
            description: 'Gestión de flujos de trabajo, seguimiento de progreso',
            capabilities: [
                'Creación de flujos de trabajo',
                'Gestión de dependencias entre tareas',
                'Seguimiento de progreso',
                'Optimización de secuencias de tareas'
            ]
        },
        'code': {
            name: 'Agente de Código',
            description: 'Generación y optimización de código, análisis estático',
            capabilities: [
                'Optimización de código existente',
                'Análisis de calidad y complejidad',
                'Generación de código basado en requisitos',
                'Detección de bugs potenciales'
            ]
        }
    };

    // Chat history
    let conversations = {};
    let currentAgent = '';

    // Update agent info
    function updateAgentInfo(agentId) {
        if (!agentId || !agentDescriptions[agentId]) {
            agentInfo.innerHTML = \`
                <div class="agent-info-placeholder">
                    <p>Selecciona un agente para ver su información</p>
                </div>
            \`;
            return;
        }
        
        const agent = agentDescriptions[agentId];
        
        agentInfo.innerHTML = \`
            <h4>\${agent.name}</h4>
            <p class="agent-description">\${agent.description}</p>
            <div class="agent-capabilities">
                <h5>Capacidades:</h5>
                <ul>
                    \${agent.capabilities.map(cap => \`<li>\${cap}</li>\`).join('')}
                </ul>
            </div>
        \`;
    }

    // Update chat title
    function updateChatTitle(agentId) {
        if (!agentId || !agentDescriptions[agentId]) {
            chatTitle.textContent = 'Chat con Agentes';
            return;
        }
        
        chatTitle.textContent = \`Chat con \${agentDescriptions[agentId].name}\`;
    }

    // Update chat history list
    function updateChatHistory() {
        chatHistory.innerHTML = '';
        
        Object.keys(conversations).forEach(agentId => {
            if (conversations[agentId].messages.length > 0) {
                const historyItem = document.createElement('li');
                historyItem.textContent = agentDescriptions[agentId]?.name || agentId;
                historyItem.dataset.agentId = agentId;
                
                if (agentId === currentAgent) {
                    historyItem.classList.add('active');
                }
                
                historyItem.addEventListener('click', function() {
                    loadConversation(agentId);
                    agentSelect.value = agentId;
                    updateAgentInfo(agentId);
                    updateChatTitle(agentId);
                });
                
                chatHistory.appendChild(historyItem);
            }
        });
        
        if (chatHistory.children.length === 0) {
            const emptyItem = document.createElement('li');
            emptyItem.textContent = 'No hay conversaciones';
            emptyItem.classList.add('empty');
            chatHistory.appendChild(emptyItem);
        }
    }

    // Load conversation
    function loadConversation(agentId) {
        if (!conversations[agentId]) {
            conversations[agentId] = {
                messages: []
            };
        }
        
        currentAgent = agentId;
        
        // Clear chat messages
        chatMessages.innerHTML = '';
        
        // Add welcome message if no messages
        if (conversations[agentId].messages.length === 0) {
            chatMessages.innerHTML = \`
                <div class="welcome-message">
                    <h3>Bienvenido al Chat con \${agentDescriptions[agentId]?.name || agentId}</h3>
                    <p>\${agentDescriptions[agentId]?.description || 'Comienza a chatear para interactuar con este agente.'}</p>
                </div>
            \`;
            return;
        }
        
        // Add messages
        conversations[agentId].messages.forEach(msg => {
            addMessageToUI(msg.type, msg.content);
        });
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add message to UI
    function addMessageToUI(type, content) {
        // Remove welcome message if present
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = \`message \${type}-message\`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add message to conversation
    function addMessageToConversation(agentId, type, content) {
        if (!conversations[agentId]) {
            conversations[agentId] = {
                messages: []
            };
        }
        
        conversations[agentId].messages.push({
            type,
            content,
            timestamp: Date.now()
        });
        
        // Update chat history
        updateChatHistory();
    }

    // Clear current conversation
    function clearCurrentConversation() {
        if (currentAgent && conversations[currentAgent]) {
            conversations[currentAgent].messages = [];
            loadConversation(currentAgent);
            updateChatHistory();
        }
    }

    // Export current conversation
    function exportCurrentConversation() {
        if (!currentAgent || !conversations[currentAgent] || conversations[currentAgent].messages.length === 0) {
            alert('No hay conversación para exportar');
            return;
        }
        
        const agentName = agentDescriptions[currentAgent]?.name || currentAgent;
        const conversation = conversations[currentAgent];
        
        // Format conversation as text
        let conversationText = \`Conversación con \${agentName}\\n\`;
        conversationText += \`Fecha: \${new Date().toLocaleString()}\\n\\n\`;
        
        conversation.messages += `Fecha: ${new Date().toLocaleString()}\n\n`;
        
        conversation.messages.forEach(msg => {
            const sender = msg.type === 'user' ? 'Usuario' : agentName;
            conversationText += `${sender}: ${msg.content}\n`;
        });
        
        // Create download link
        const blob = new Blob([conversationText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversacion_${currentAgent}_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Event listeners
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            const selectedAgent = agentSelect.value;

            if (message && selectedAgent) {
                // Add user message to chat
                addMessageToUI('user', message);
                addMessageToConversation(selectedAgent, 'user', message);

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
                    addMessageToUI('agent', data.response);
                    addMessageToConversation(selectedAgent, 'agent', data.response);
                    
                    if (data.task_id) {
                        // Poll for task updates
                        const pollInterval = setInterval(() => {
                            fetch(`/api/tasks/${data.task_id}`)
                                .then(response => response.json())
                                .then(taskData => {
                                    if (taskData.status === 'completed' && taskData.result) {
                                        const resultText = typeof taskData.result === 'object' 
                                            ? JSON.stringify(taskData.result, null, 2)
                                            : taskData.result;
                                        addMessageToUI('agent', resultText);
                                        addMessageToConversation(selectedAgent, 'agent', resultText);
                                        clearInterval(pollInterval);
                                    } else if (taskData.status === 'failed') {
                                        addMessageToUI('agent', 'Lo siento, hubo un error al procesar tu solicitud.');
                                        addMessageToConversation(selectedAgent, 'agent', 'Lo siento, hubo un error al procesar tu solicitud.');
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
                    addMessageToUI('agent', 'Lo siento, hubo un error al procesar tu solicitud.');
                    addMessageToConversation(selectedAgent, 'agent', 'Lo siento, hubo un error al procesar tu solicitud.');
                });

                messageInput.value = '';
            }
        });
    }
    
    if (agentSelect) {
        agentSelect.addEventListener('change', function() {
            const selectedAgent = this.value;
            if (selectedAgent) {
                currentAgent = selectedAgent;
                updateAgentInfo(selectedAgent);
                updateChatTitle(selectedAgent);
                loadConversation(selectedAgent);
            }
        });
    }
    
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearCurrentConversation);
    }
    
    if (exportChatBtn) {
        exportChatBtn.addEventListener('click', exportCurrentConversation);
    }

    // Initialize
    updateAgentInfo('');
    updateChatHistory();
});`;

console.log("Archivo chat.js actualizado con gestión de conversaciones y exportación.");

// 3.5. web/static/js/settings.js
const settingsJs = `document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const generalSettingsForm = document.getElementById('general-settings-form');
    const apiSettingsForm = document.getElementById('api-settings-form');
    const agentSettingsForm = document.getElementById('agent-settings-form');
    const advancedSettingsForm = document.getElementById('advanced-settings-form');
    const showApiKeyBtn = document.getElementById('show-api-key');
    const apiKeyInput = document.getElementById('api-key');

    // Fetch settings
    function fetchSettings() {
        fetch('/api/settings')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch settings');
                }
                return response.json();
            })
            .then(data => {
                // Populate general settings
                if (data.general) {
                    document.getElementById('system-name').value = data.general.system_name || 'Tío Pepe';
                    document.getElementById('log-level').value = data.general.log_level || 'info';
                    document.getElementById('language').value = data.general.language || 'es';
                }
                
                // Populate API settings
                if (data.api) {
                    document.getElementById('api-url').value = data.api.url || 'http://localhost:5000';
                    document.getElementById('api-key').value = data.api.key || '••••••••••••••••';
                    document.getElementById('api-timeout').value = data.api.timeout || 30;
                }
                
                // Populate agent settings
                if (data.agents) {
                    document.getElementById('agent-timeout').value = data.agents.timeout || 30;
                    document.getElementById('max-agents').value = data.agents.max_concurrent || 5;
                    
                    if (data.agents.enabled) {
                        document.getElementById('enable-nlp').checked = data.agents.enabled.nlp !== false;
                        document.getElementById('enable-vision').checked = data.agents.enabled.vision !== false;
                        document.getElementById('enable-web').checked = data.agents.enabled.web !== false;
                        document.getElementById('enable-data').checked = data.agents.enabled.data !== false;
                        document.getElementById('enable-planning').checked = data.agents.enabled.planning !== false;
                        document.getElementById('enable-code').checked = data.agents.enabled.code !== false;
                    }
                }
                
                // Populate advanced settings
                if (data.advanced) {
                    document.getElementById('memory-limit').value = data.advanced.memory_limit || 1024;
                    document.getElementById('storage-path').value = data.advanced.storage_path || './data';
                    document.getElementById('debug-mode').checked = data.advanced.debug_mode === true;
                }
            })
            .catch(error => {
                console.error('Error fetching settings:', error);
                showNotification('Error al cargar la configuración', 'error');
            });
    }

    // Save settings
    function saveSettings(section, data) {
        fetch(\`/api/settings/\${section}\`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(\`Failed to save \${section} settings\`);
            }
            return response.json();
        })
        .then(data => {
            showNotification(\`Configuración de \${section} guardada correctamente\`, 'success');
        })
        .catch(error => {
            console.error(\`Error saving \${section} settings:\`, error);
            showNotification(\`Error al guardar la configuración de \${section}\`, 'error');
        });
    }

    // Show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = \`notification \${type}\`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Tab navigation
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to current button and pane
            this.classList.add('active');
            document.getElementById(\`\${tabId}-tab\`).classList.add('active');
        });
    });

    // Show/hide API key
    if (showApiKeyBtn && apiKeyInput) {
        showApiKeyBtn.addEventListener('click', function() {
            if (apiKeyInput.type === 'password') {
                apiKeyInput.type = 'text';
                this.textContent = 'Ocultar';
            } else {
                apiKeyInput.type = 'password';
                this.textContent = 'Mostrar';
            }
        });
    }

    // Form submissions
    if (generalSettingsForm) {
        generalSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const data = {
                system_name: document.getElementById('system-name').value,
                log_level: document.getElementById('log-level').value,
                language: document.getElementById('language').value
            };
            
            saveSettings('general', data);
        });
    }
    
    if (apiSettingsForm) {
        apiSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const data = {
                url: document.getElementById('api-url').value,
                timeout: parseInt(document.getElementById('api-timeout').value)
            };
            
            // Only include API key if it's not masked
            if (apiKeyInput.type === 'text') {
                data.key = apiKeyInput.value;
            }
            
            saveSettings('api', data);
        });
    }
    
    if (agentSettingsForm) {
        agentSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const data = {
                timeout: parseInt(document.getElementById('agent-timeout').value),
                max_concurrent: parseInt(document.getElementById('max-agents').value),
                enabled: {
                    nlp: document.getElementById('enable-nlp').checked,
                    vision: document.getElementById('enable-vision').checked,
                    web: document.getElementById('enable-web').checked,
                    data: document.getElementById('enable-data').checked,
                    planning: document.getElementById('enable-planning').checked,
                    code: document.getElementById('enable-code').checked
                }
            };
            
            saveSettings('agents', data);
        });
    }
    
    if (advancedSettingsForm) {
        advancedSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const data = {
                memory_limit: parseInt(document.getElementById('memory-limit').value),
                storage_path: document.getElementById('storage-path').value,
                debug_mode: document.getElementById('debug-mode').checked
            };
            
            saveSettings('advanced', data);
        });
    }

    // Initial fetch
    fetchSettings();
});`;

console.log("Archivo settings.js actualizado con gestión de pestañas y notificaciones.");

// 3.6. web/static/js/error.js
const errorJs = `document.addEventListener('DOMContentLoaded', function() {
    // Log error to console for debugging
    console.error('Page error:', window.location.pathname);
    
    // Add event listener to the "Go Back" button
    const goBackBtn = document.querySelector('button.secondary');
    if (goBackBtn) {
        goBackBtn.addEventListener('click', function() {
            history.back();
        });
    }
    
    // Add event listener to the "Go to Dashboard" button
    const dashboardBtn = document.querySelector('a.primary');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', function(e) {
            // No need for additional logic, the link will work as is
        });
    }
    
    // Animate error icon
    const errorIcon = document.querySelector('.error-icon svg');
    if (errorIcon) {
        errorIcon.classList.add('pulse');
    }
});`;

console.log("Archivo error.js actualizado con animación de icono.");

console.log("\n=== INSTRUCCIONES DE IMPLEMENTACIÓN ===");
console.log("Para implementar estos cambios, sigue estos pasos:");
console.log("");
console.log("1. Actualiza los archivos HTML en la carpeta web/templates/:");
console.log("   - index.html");
console.log("   - agents.html");
console.log("   - tasks.html");
console.log("   - chat.html");
console.log("   - settings.html");
console.log("   - 404.html");
console.log("   - 500.html");
console.log("");
console.log("2. Actualiza el archivo CSS en web/static/css/:");
console.log("   - style.css");
console.log("");
console.log("3. Actualiza los archivos JavaScript en web/static/js/:");
console.log("   - dashboard.js");
console.log("   - agents.js");
console.log("   - tasks.js");
console.log("   - chat.js");
console.log("   - settings.js");
console.log("   - error.js");
console.log("");
console.log("4. Asegúrate de que la estructura de directorios sea correcta:");
console.log("   - web/");
console.log("     - templates/");
console.log("     - static/");
console.log("       - css/");
console.log("       - js/");
console.log("");
console.log("5. Reinicia el servidor web para aplicar los cambios");
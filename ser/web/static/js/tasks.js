// Creación de tasks.js

const tasksJs = `document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tasksTable = document.getElementById('tasks-table');
    const tasksBody = document.getElementById('tasks-body');
    const newTaskBtn = document.getElementById('new-task-btn');
    const taskModal = document.getElementById('task-modal');
    const taskForm = document.getElementById('task-form');
    const cancelTaskBtn = document.getElementById('cancel-task');
    const taskStatusFilter = document.getElementById('task-status-filter');

    // Fetch tasks
    function fetchTasks() {
        // Get filter value
        const statusFilter = taskStatusFilter.value;
        let url = '/api/tasks';
        if (statusFilter !== 'all') {
            url += \`?status=\${statusFilter}\`;
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
                    emptyRow.innerHTML = '<td colspan="5" class="text-center">No tasks found</td>';
                    tasksBody.appendChild(emptyRow);
                }
            })
            .catch(error => {
                console.error('Error fetching tasks:', error);
                tasksBody.innerHTML = '<tr><td colspan="5" class="text-center error-message">Failed to load tasks</td></tr>';
            });
    }

    // Add task row to table
    function addTaskRow(task) {
        const row = document.createElement('tr');
        
        // Format date
        const date = new Date(task.created_at * 1000);
        const formattedDate = date.toLocaleString();
        
        row.innerHTML = \`
            <td>\${task.id}</td>
            <td>\${task.type}</td>
            <td><span class="status-\${task.status}">\${task.status}</span></td>
            <td>\${formattedDate}</td>
            <td>
                <button class="btn btn-sm view-task" data-task-id="\${task.id}">View</button>
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
                // In a real implementation, we would show a modal with task details
                console.log('Task details:', task);
                alert(\`Task ID: \${task.id}\\nType: \${task.type}\\nStatus: \${task.status}\`);
            })
            .catch(error => {
                console.error('Error fetching task details:', error);
                alert('Failed to load task details');
            });
    }

    // Initial fetch
    fetchTasks();
    
    // Refresh data every 10 seconds
    setInterval(fetchTasks, 10000);

    // Task modal functionality is disabled in view-only mode
    // but we'll add the event listeners anyway for completeness
    
    // Open task modal
    newTaskBtn.addEventListener('click', function() {
        taskModal.style.display = 'block';
    });
    
    // Close task modal
    cancelTaskBtn.addEventListener('click', function() {
        taskModal.style.display = 'none';
    });
    
    // Submit task form
    taskForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // This would submit the form data to create a new task
        taskModal.style.display = 'none';
    });
    
    // Filter tasks
    taskStatusFilter.addEventListener('change', fetchTasks);
});`;

console.log("Archivo tasks.js creado con lógica para gestionar tareas.");
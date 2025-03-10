// Main JavaScript file for Tío Pepe dashboard

// Dashboard metrics update
function updateDashboardMetrics() {
    fetch('/api/dashboard/metrics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('active-tasks').textContent = data.active_tasks;
            document.getElementById('active-agents').textContent = data.active_agents;
            document.getElementById('system-status').textContent = data.system_status;
        })
        .catch(error => console.error('Error fetching metrics:', error));
}

// Activity list update
function updateActivityList() {
    fetch('/api/activity')
        .then(response => response.json())
        .then(data => {
            const activityList = document.getElementById('activity-list');
            activityList.innerHTML = '';
            
            data.activities.forEach(activity => {
                const date = new Date(activity.timestamp * 1000);
                const listItem = document.createElement('a');
                listItem.href = '#';
                listItem.className = 'list-group-item list-group-item-action';
                listItem.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <p class="mb-1">${activity.description}</p>
                        <small>${date.toLocaleString()}</small>
                    </div>
                `;
                activityList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching activities:', error));
}

// Initialize dashboard
function initializeDashboard() {
    updateDashboardMetrics();
    updateActivityList();
    
    // Update metrics every 30 seconds
    setInterval(updateDashboardMetrics, 30000);
    // Update activity list every minute
    setInterval(updateActivityList, 60000);
}

// Start dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDashboard);
document.addEventListener('DOMContentLoaded', function() {
    // Fetch current settings
    fetch('/api/settings')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch settings');
            }
            return response.json();
        })
        .then(data => {
            console.log('Settings loaded:', data);
            // In a real implementation, we would populate the form fields
            // For now, we'll just log the data
        })
        .catch(error => {
            console.error('Error:', error);
        });

    // Add event listeners for form submissions
    // These are disabled in the current view-only mode
    document.getElementById('general-settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        // This would submit the form data to the server
    });

    document.getElementById('api-settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        // This would submit the form data to the server
    });

    document.getElementById('agent-settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        // This would submit the form data to the server
    });
});
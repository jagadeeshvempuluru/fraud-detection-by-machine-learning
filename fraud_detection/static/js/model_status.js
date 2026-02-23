document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Setup CSRF token for AJAX requests
    const csrftoken = getCookie('csrftoken');

    // Handle toggle switches
    document.querySelectorAll('.model-status-toggle').forEach(function(toggle) {
        toggle.addEventListener('change', function(e) {
            const modelId = this.dataset.modelId;
            const isActive = this.checked;

            fetch(`/toggle-model-status/${modelId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    is_active: isActive
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI to reflect the change
                    const statusText = this.closest('tr').querySelector('.model-status-text');
                    if (statusText) {
                        statusText.textContent = isActive ? 'Active' : 'Inactive';
                        statusText.className = `model-status-text ${isActive ? 'text-success' : 'text-danger'}`;
                    }
                } else {
                    // Revert toggle if there was an error
                    this.checked = !isActive;
                    console.error('Failed to update model status:', data.error);
                    alert('Failed to update model status. Please try again.');
                }
            })
            .catch(error => {
                // Revert toggle and show error message
                this.checked = !isActive;
                console.error('Error updating model status:', error);
                alert('An error occurred while updating the model status. Please try again.');
            });
        });
    });
});
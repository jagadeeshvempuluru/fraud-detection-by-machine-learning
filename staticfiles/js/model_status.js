document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.querySelectorAll('.model-status-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const modelId = this.dataset.modelId;
            const isActive = this.dataset.isActive === 'true';
            const newStatus = !isActive;

            fetch(`/toggle-model-status/${modelId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    is_active: newStatus
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.classList.toggle('btn-success');
                    this.classList.toggle('btn-secondary');
                    this.textContent = newStatus ? 'Active' : 'Inactive';
                    this.dataset.isActive = newStatus.toString();
                } else {
                    alert('Failed to update model status');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating model status');
            });
        });
    });
});
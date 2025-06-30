document.getElementById('answer-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        const formData = new FormData(this);
        const response = await fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        if (response.ok) {
            // Handle success
            showMessage(data.message, 'success');
            if (data.status === 'success') {
                location.reload();
            }
        } else {
            // Handle error
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An error occurred. Please try again.', 'error');
    }
});
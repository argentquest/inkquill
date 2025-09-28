document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('basic-story-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        
        // Get form data
        const formData = {
            title: document.getElementById('title').value.trim(),
            short_description: document.getElementById('short_description').value.trim()
        };
        
        // Validate
        if (!formData.title) {
            if (typeof showToast === 'function') showToast('error', 'Please enter a story title');
            else alert('Please enter a story title');
            return;
        }
        
        // Disable button and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating your story...';
        
        try {
            const response = await fetch('/api/v1/stories/basic/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to create story');
            }
            
            if (typeof showToast === 'function') showToast('success', 'Basic Story created! Taking you to the editor...');
            
            // Use the URL from the API response for a robust redirect
            if (!result.editor_url) {
                throw new Error('API did not provide a redirect URL.');
            }
            
            setTimeout(() => { window.location.href = result.editor_url; }, 500);
            
        } catch (error) {
            console.error('Error creating Basic Story:', error);
            if (typeof showToast === 'function') showToast('error', error.message || 'Failed to create story. Please try again.');
            else alert(error.message || 'Failed to create story. Please try again.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
});

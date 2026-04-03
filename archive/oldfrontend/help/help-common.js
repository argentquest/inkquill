// Common JavaScript functionality for help pages

// Copy to clipboard function
function copyToClipboard(button, text) {
    navigator.clipboard.writeText(text).then(() => {
        // Store original text
        const originalText = button.textContent;
        
        // Change button text and style
        button.textContent = 'Copied!';
        button.classList.add('copied');
        
        // Reset after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        button.textContent = 'Failed to copy';
        setTimeout(() => {
            button.textContent = 'Copy';
        }, 2000);
    });
}

// Initialize collapsible sections
document.addEventListener('DOMContentLoaded', function() {
    // Setup collapsible sections
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    collapsibleHeaders.forEach(header => {
        header.addEventListener('click', function() {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            content.classList.toggle('active');
        });
    });
    
    // Setup tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabGroup = this.getAttribute('data-tab-group');
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs in group
            document.querySelectorAll(`.tab-button[data-tab-group="${tabGroup}"]`).forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelectorAll(`.tab-content[data-tab-group="${tabGroup}"]`).forEach(content => {
                content.classList.remove('active');
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            document.querySelector(`.tab-content[data-tab-group="${tabGroup}"][data-tab="${tabId}"]`).classList.add('active');
        });
    });
    
    // Setup search functionality if search box exists
    const searchInput = document.querySelector('.help-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const sections = document.querySelectorAll('.help-section');
            
            sections.forEach(section => {
                const text = section.textContent.toLowerCase();
                if (text.includes(searchTerm) || searchTerm === '') {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });
        });
    }
});

// Function to highlight code syntax (basic)
function highlightCode() {
    const codeBlocks = document.querySelectorAll('.code-block pre');
    codeBlocks.forEach(block => {
        let html = block.innerHTML;
        // Basic syntax highlighting
        html = html.replace(/(".*?")/g, '<span style="color: #a8e6cf;">$1</span>'); // strings
        html = html.replace(/(\b\d+\b)/g, '<span style="color: #ffd3b6;">$1</span>'); // numbers
        html = html.replace(/(\b(?:def|class|import|from|return|if|else|for|while|try|except|with|as)\b)/g, '<span style="color: #ffaaa5;">$1</span>'); // keywords
        block.innerHTML = html;
    });
}

// Run syntax highlighting on load
document.addEventListener('DOMContentLoaded', highlightCode);
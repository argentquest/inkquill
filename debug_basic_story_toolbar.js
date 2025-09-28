// Debug script to check basic story editor toolbar
console.log('=== Basic Story Editor Toolbar Debug ===');

// Check if AIQuillToolbar is loaded
console.log('AIQuillToolbar available:', typeof AIQuillToolbar !== 'undefined');

// Check if quill is initialized
console.log('Quill instance:', window.quill ? 'Found' : 'Not found');

// Check toolbar structure
const toolbar = document.querySelector('.ql-toolbar');
console.log('Toolbar found:', !!toolbar);
if (toolbar) {
    console.log('Toolbar HTML:', toolbar.innerHTML);
    const formatGroups = toolbar.querySelectorAll('.ql-formats');
    console.log('Format groups found:', formatGroups.length);
    formatGroups.forEach((group, index) => {
        console.log(`Group ${index}:`, group.innerHTML);
    });
}

// Check if AI button exists
const aiButton = document.querySelector('.ql-ai-transform');
console.log('AI button found:', !!aiButton);

// Check for any errors in console
console.log('=== End Debug ===');
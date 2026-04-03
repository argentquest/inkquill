// /story_app/app/static/js/location_form_resize.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Location Form Resize: DOMContentLoaded event fired.");

    // DOM elements
    const formLayout = document.getElementById('form-layout');
    const sidebar = document.getElementById('form-sidebar');
    const resizeHandle = document.getElementById('form-resize-handle');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    // Initialize sidebar state
    let sidebarCollapsed = false;

    // Setup event listeners
    setupSidebarToggle();
    setupSidebarResize();

    function setupSidebarToggle() {
        if (!sidebarToggle) return;

        sidebarToggle.addEventListener('click', () => {
            sidebarCollapsed = !sidebarCollapsed;
            
            if (sidebarCollapsed) {
                formLayout.classList.add('sidebar-collapsed');
                sidebarToggle.innerHTML = '<i class="fas fa-chevron-left"></i>';
                sidebarToggle.title = 'Show Advanced Features';
            } else {
                formLayout.classList.remove('sidebar-collapsed');
                sidebarToggle.innerHTML = '<i class="fas fa-cog"></i>';
                sidebarToggle.title = 'Hide Advanced Features';
            }
        });
    }

    function setupSidebarResize() {
        if (!resizeHandle || !sidebar) return;

        let isResizing = false;

        // Drag resize handle
        resizeHandle.addEventListener('mousedown', (e) => {
            if (sidebarCollapsed) return;
            
            isResizing = true;
            document.body.style.cursor = 'col-resize';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing || sidebarCollapsed) return;

            const containerRect = formLayout.getBoundingClientRect();
            const newWidth = containerRect.right - e.clientX;
            const clampedWidth = Math.max(300, Math.min(600, newWidth));
            
            sidebar.style.width = clampedWidth + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
            }
        });
    }

    console.log("Location form resize functionality initialized");
});

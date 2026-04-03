// /story_app/app/static/js/notifications.js

/**
 * notifications.js
 * ----------------
 * Helper functions for displaying Bootstrap Toasts for user notifications.
 */

"use strict";

/**
 * Displays a Bootstrap Toast notification.
 * @param {string} message - The message to display in the toast.
 * @param {string} type - The type of toast ('success', 'error', 'info', 'warning'). Defaults to 'info'.
 * @param {number} delay - How long the toast should be visible in milliseconds. Defaults to 5000ms.
 */
function showToast(message, type = 'info', delay = 5000) {
    const toastContainer = document.querySelector('.toast-container'); // This is in base.html
    if (!toastContainer) {
        console.error("Toast container not found in base.html. Cannot display toast. Falling back to alert.");
        alert(`${type.toUpperCase()}: ${message}`);
        return;
    }

    // Determine background color class and icon based on type
    let bgClass = 'bg-info'; 
    let textClass = 'text-white'; 
    let iconHtml = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle-fill me-2" viewBox="0 0 16 16"><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2"/></svg>';

    switch (type.toLowerCase()) {
        case 'success':
            bgClass = 'bg-success';
            iconHtml = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle-fill me-2" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>';
            break;
        case 'error':
            bgClass = 'bg-danger';
            iconHtml = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2"/></svg>';
            break;
        case 'warning':
            bgClass = 'bg-warning';
            textClass = 'text-dark'; // Dark text for light warning background
            iconHtml = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2"/></svg>';
            break;
    }

    const toastId = 'toast-' + Date.now() + Math.random().toString(36).substring(2,7); // More unique ID

    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} ${textClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="${delay}">
            <div class="d-flex">
                <div class="toast-body">
                    ${iconHtml}
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = document.getElementById(toastId);
    if (toastElement) {
        const toastInstance = new bootstrap.Toast(toastElement, { delay: delay }); // Pass delay option
        
        toastElement.addEventListener('hidden.bs.toast', function () {
            toastElement.remove();
        });
        
        toastInstance.show();
        console.log(`Toast shown: ${message} (Type: ${type})`);
    } else {
        console.error(`Failed to find toast element with ID ${toastId} after insertion.`);
    }
}


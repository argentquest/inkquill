// /ai_rag_story_app/app/static/js/maintenance.js

/**
 * Maintenance mode notification system
 * Checks for maintenance status and shows toast notifications to users
 */

"use strict";

class MaintenanceNotifier {
    constructor() {
        this.checkInterval = 60000; // Check every minute
        this.intervalId = null;
        this.lastMaintenanceStatus = false;
        this.currentToastId = null;
    }

    /**
     * Start monitoring maintenance status
     */
    start() {
        // Check immediately on start
        this.checkMaintenanceStatus();
        
        // Set up periodic checking
        this.intervalId = setInterval(() => {
            this.checkMaintenanceStatus();
        }, this.checkInterval);
        
        console.log('Maintenance status monitoring started');
    }

    /**
     * Stop monitoring maintenance status
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        console.log('Maintenance status monitoring stopped');
    }

    /**
     * Check maintenance status from the API
     */
    async checkMaintenanceStatus() {
        try {
            const response = await fetch('/api/v1/maintenance/status');
            if (!response.ok) {
                console.warn('Failed to check maintenance status:', response.status);
                return;
            }

            const data = await response.json();
            this.handleMaintenanceStatus(data);
        } catch (error) {
            console.warn('Error checking maintenance status:', error);
        }
    }

    /**
     * Handle maintenance status response
     */
    handleMaintenanceStatus(data) {
        const isMaintenanceActive = data.enabled;
        const message = data.message;
        const estimatedEndTime = data.estimated_end_time;

        // If maintenance just became active
        if (isMaintenanceActive && !this.lastMaintenanceStatus) {
            this.showMaintenanceToast(message, estimatedEndTime);
        }
        
        // If maintenance just ended
        else if (!isMaintenanceActive && this.lastMaintenanceStatus) {
            this.hideMaintenanceToast();
            this.showToast('🎉 System update completed! The application is now fully operational.', 'success', 8000);
        }

        this.lastMaintenanceStatus = isMaintenanceActive;
    }

    /**
     * Show maintenance notification toast
     */
    showMaintenanceToast(message, estimatedEndTime) {
        // Format the message with time info if available
        let fullMessage = message || "The application is getting an update and will be back in about 5 minutes.";
        
        if (estimatedEndTime) {
            const endTime = new Date(estimatedEndTime);
            const now = new Date();
            const minutesRemaining = Math.max(0, Math.ceil((endTime - now) / (1000 * 60)));
            
            if (minutesRemaining > 0) {
                fullMessage += ` Estimated completion: ${minutesRemaining} minute${minutesRemaining !== 1 ? 's' : ''}.`;
            }
        }

        // Show persistent toast (very long duration)
        this.showToast(
            `🔧 ${fullMessage}`,
            'warning',
            300000 // 5 minutes duration
        );

        console.log('Maintenance mode notification shown');
    }

    /**
     * Hide maintenance toast (if needed)
     */
    hideMaintenanceToast() {
        // The toast system will handle hiding automatically
        console.log('Maintenance mode ended');
    }

    /**
     * Show a toast notification (wrapper for the global showToast function)
     */
    showToast(message, type = 'info', delay = 5000) {
        if (typeof showToast === 'function') {
            showToast(message, type, delay);
        } else {
            console.warn('showToast function not available, falling back to alert');
            alert(message);
        }
    }

    /**
     * Manual trigger for admin testing
     */
    async enableMaintenanceMode(message = null, durationMinutes = 5) {
        try {
            const params = new URLSearchParams();
            if (message) params.append('message', message);
            params.append('duration_minutes', durationMinutes);

            const response = await fetch('/api/v1/maintenance/enable', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params
            });

            if (response.ok) {
                this.showToast('Maintenance mode enabled', 'success');
                // Force immediate check
                setTimeout(() => this.checkMaintenanceStatus(), 1000);
            } else {
                this.showToast('Failed to enable maintenance mode', 'error');
            }
        } catch (error) {
            console.error('Error enabling maintenance mode:', error);
            this.showToast('Error enabling maintenance mode', 'error');
        }
    }

    /**
     * Manual disable for admin testing
     */
    async disableMaintenanceMode() {
        try {
            const response = await fetch('/api/v1/maintenance/disable', {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Maintenance mode disabled', 'success');
                // Force immediate check
                setTimeout(() => this.checkMaintenanceStatus(), 1000);
            } else {
                this.showToast('Failed to disable maintenance mode', 'error');
            }
        } catch (error) {
            console.error('Error disabling maintenance mode:', error);
            this.showToast('Error disabling maintenance mode', 'error');
        }
    }
}

// Global instance
window.maintenanceNotifier = new MaintenanceNotifier();

// Auto-start when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.maintenanceNotifier.start();
});

// Expose functions for admin console testing
window.enableMaintenance = function(message, duration) {
    window.maintenanceNotifier.enableMaintenanceMode(message, duration);
};

window.disableMaintenance = function() {
    window.maintenanceNotifier.disableMaintenanceMode();
};
// /ai_rag_story_app/app/static/js/image_job_monitor.js
"use strict";

/**
 * Global image job monitor that tracks pending jobs across page navigation
 * This script should be included in the base layout to work on all pages
 */

class ImageJobMonitor {
    constructor() {
        this.checkInterval = 10000; // Check every 10 seconds
        this.intervalId = null;
        this.isChecking = false;
    }

    /**
     * Start monitoring for pending image jobs
     */
    start() {
        // Check immediately
        this.checkPendingJobs();
        
        // Then check periodically
        this.intervalId = setInterval(() => {
            this.checkPendingJobs();
        }, this.checkInterval);
    }

    /**
     * Stop monitoring
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Check for pending image generation jobs
     */
    async checkPendingJobs() {
        if (this.isChecking) return; // Prevent concurrent checks
        
        this.isChecking = true;
        
        try {
            // Get tracked jobs from localStorage
            const trackedJobs = this.getTrackedJobs();
            if (trackedJobs.length === 0) {
                this.isChecking = false;
                return;
            }

            // Check status of tracked jobs
            for (const jobId of trackedJobs) {
                await this.checkJobStatus(jobId);
            }
            
        } catch (error) {
            console.error('Error checking pending jobs:', error);
        } finally {
            this.isChecking = false;
        }
    }

    /**
     * Check status of a specific job
     */
    async checkJobStatus(jobId) {
        try {
            const response = await fetch(`/api/v1/images/job/${jobId}/status`, {
                credentials: 'include'
            });

            if (!response.ok) {
                // Job not found or error - remove from tracking
                this.removeTrackedJob(jobId);
                return;
            }

            const job = await response.json();

            if (job.state === "COMPLETED") {
                // Show success notification
                this.showNotification(
                    "Image Generation Complete!",
                    "Your image has been generated successfully. Click to view.",
                    'success',
                    () => {
                        // Get the element type and ID from job metadata
                        if (job.result && job.result.element_type && job.result.element_id) {
                            // Navigate to the element page
                            window.location.href = `/ui/worlds/${job.result.element_type}s/${job.result.element_id}`;
                        }
                    }
                );
                
                // Remove from tracking
                this.removeTrackedJob(jobId);
                
            } else if (job.state === "FAILED") {
                // Show error notification
                this.showNotification(
                    "Image Generation Failed",
                    job.status_message || "The image generation failed. Please try again.",
                    'error'
                );
                
                // Remove from tracking
                this.removeTrackedJob(jobId);
            }
            // If PENDING or RUNNING, keep tracking
            
        } catch (error) {
            console.error(`Error checking job ${jobId}:`, error);
        }
    }

    /**
     * Add a job to tracking
     */
    addTrackedJob(jobId, elementType, elementId) {
        const tracked = this.getTrackedJobs();
        if (!tracked.includes(jobId)) {
            tracked.push(jobId);
            
            // Store job metadata
            const jobMeta = this.getJobMetadata();
            jobMeta[jobId] = {
                elementType,
                elementId,
                startTime: new Date().toISOString()
            };
            
            localStorage.setItem('imageJobsTracking', JSON.stringify(tracked));
            localStorage.setItem('imageJobsMetadata', JSON.stringify(jobMeta));
        }
    }

    /**
     * Remove a job from tracking
     */
    removeTrackedJob(jobId) {
        const tracked = this.getTrackedJobs();
        const filtered = tracked.filter(id => id !== jobId);
        localStorage.setItem('imageJobsTracking', JSON.stringify(filtered));
        
        // Remove metadata
        const jobMeta = this.getJobMetadata();
        delete jobMeta[jobId];
        localStorage.setItem('imageJobsMetadata', JSON.stringify(jobMeta));
    }

    /**
     * Get list of tracked job IDs
     */
    getTrackedJobs() {
        try {
            const stored = localStorage.getItem('imageJobsTracking');
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    /**
     * Get job metadata
     */
    getJobMetadata() {
        try {
            const stored = localStorage.getItem('imageJobsMetadata');
            return stored ? JSON.parse(stored) : {};
        } catch {
            return {};
        }
    }

    /**
     * Show a notification (toast or browser notification)
     */
    showNotification(title, message, type = 'info', onClick = null) {
        // First try to show a toast if the function exists
        if (typeof showToast === 'function') {
            showToast(`${title}: ${message}`, type, 10000);
        }

        // Also try browser notifications if permitted
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(title, {
                body: message,
                icon: '/static/img/favicon.ico',
                tag: 'image-generation',
                requireInteraction: false
            });

            if (onClick) {
                notification.onclick = function() {
                    window.focus();
                    onClick();
                    notification.close();
                };
            }

            // Auto close after 10 seconds
            setTimeout(() => notification.close(), 10000);
        }
    }

    /**
     * Request notification permission
     */
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        }
    }

    /**
     * Get count of pending jobs
     */
    getPendingJobCount() {
        return this.getTrackedJobs().length;
    }

    /**
     * Show pending jobs indicator in UI
     */
    updatePendingJobsIndicator() {
        const count = this.getPendingJobCount();
        const indicator = document.getElementById('pending-image-jobs-indicator');
        
        if (indicator) {
            if (count > 0) {
                indicator.innerHTML = `
                    <span class="badge bg-warning text-dark">
                        <i class="fas fa-image fa-spin me-1"></i>${count} Image${count !== 1 ? 's' : ''} Generating
                    </span>
                `;
                indicator.style.display = 'inline-block';
            } else {
                indicator.style.display = 'none';
            }
        }
    }
}

// Create global instance
window.imageJobMonitor = new ImageJobMonitor();

// Start monitoring when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Request notification permission on first interaction
    document.addEventListener('click', () => {
        window.imageJobMonitor.requestNotificationPermission();
    }, { once: true });
    
    // Start monitoring
    window.imageJobMonitor.start();
    
    // Update UI indicator
    window.imageJobMonitor.updatePendingJobsIndicator();
    
    // Update indicator periodically
    setInterval(() => {
        window.imageJobMonitor.updatePendingJobsIndicator();
    }, 5000);
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    window.imageJobMonitor.stop();
});
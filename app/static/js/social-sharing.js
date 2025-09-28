/* ========================================================================
   SOCIAL SHARING FUNCTIONALITY
   Handles popup sharing, URL generation, and analytics tracking with coin rewards
   ======================================================================== */

class SocialSharingManager {
    constructor() {
        this.apiBaseUrl = '/api/v1/social';
        this.isInitialized = false;
        this.shareData = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.isInitialized = true;
        console.log('Social Sharing Manager initialized');
    }

    bindEvents() {
        // Listen for social share button clicks
        document.addEventListener('click', (e) => {
            const shareBtn = e.target.closest('.social-share-btn');
            if (shareBtn) {
                e.preventDefault();
                this.handleShare(shareBtn);
            }
        });

        // Listen for copy link button specifically
        document.addEventListener('click', (e) => {
            const copyBtn = e.target.closest('.social-share-btn.copy-link');
            if (copyBtn) {
                e.preventDefault();
                this.handleCopyLink(copyBtn);
            }
        });
    }

    async handleShare(button) {
        const platform = button.dataset.platform;
        const container = button.closest('.social-sharing-container');
        
        if (!container) {
            console.error('Social sharing container not found');
            return;
        }

        // Extract share data from button and container
        this.shareData = {
            content_type: container.dataset.contentType,
            content_id: container.dataset.contentId,
            content_title: button.dataset.title || '',
            content_url: button.dataset.url || window.location.href,
            platform: platform,
            shared_text: this.generateSharedText(button),
            shared_hashtags: button.dataset.hashtags || ''
        };

        // Handle copy link differently
        if (platform === 'copy_link') {
            this.handleCopyLink(button);
            return;
        }

        try {
            // Generate share URL
            const shareUrl = await this.generateShareUrl(button);
            
            // Open share popup
            this.openSharePopup(shareUrl, platform);
            
            // Track the share
            await this.trackShare();
            
        } catch (error) {
            console.error('Error handling share:', error);
            this.showFeedback(container, 'Error sharing content. Please try again.', 'error');
        }
    }

    async handleCopyLink(button) {
        const url = button.dataset.url || window.location.href;
        const container = button.closest('.social-sharing-container');
        
        try {
            // Copy to clipboard
            await navigator.clipboard.writeText(url);
            
            // Update share data for tracking
            this.shareData = {
                content_type: container.dataset.contentType,
                content_id: container.dataset.contentId,
                content_title: button.dataset.title || document.title,
                content_url: url,
                platform: 'copy_link',
                shared_text: url,
                shared_hashtags: ''
            };
            
            // Track the copy action
            const response = await this.trackShare();
            
            // Show success feedback
            this.showFeedback(
                container, 
                `Link copied! ${response.coin_awarded ? `You earned ${response.coin_amount} coin!` : ''}`,
                'success'
            );
            
        } catch (error) {
            console.error('Error copying link:', error);
            this.showFeedback(container, 'Error copying link. Please try again.', 'error');
        }
    }

    async generateShareUrl(button) {
        const platform = button.dataset.platform;
        const url = button.dataset.url || window.location.href;
        const title = button.dataset.title || document.title;
        const description = button.dataset.description || '';
        const image = button.dataset.image || '';
        const hashtags = button.dataset.hashtags || '';

        const requestData = {
            content_type: this.shareData.content_type,
            content_id: this.shareData.content_id,
            platform: platform
        };

        const params = new URLSearchParams({
            url: url,
            title: title,
            description: description,
            image: image,
            hashtags: hashtags
        });

        try {
            const response = await fetch(`${this.apiBaseUrl}/share/url?${params}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                url: data.share_url,
                width: data.popup_width,
                height: data.popup_height
            };
        } catch (error) {
            console.error('Error generating share URL:', error);
            throw error;
        }
    }

    openSharePopup(shareData, platform) {
        const { url, width, height } = shareData;
        
        // Calculate centered position
        const left = (window.screen.width / 2) - (width / 2);
        const top = (window.screen.height / 2) - (height / 2);
        
        const features = [
            `width=${width}`,
            `height=${height}`,
            `left=${left}`,
            `top=${top}`,
            'scrollbars=yes',
            'resizable=yes',
            'toolbar=no',
            'menubar=no',
            'location=no',
            'directories=no',
            'status=no'
        ].join(',');

        // Open popup window
        const popup = window.open(url, `social_share_${platform}`, features);
        
        if (!popup) {
            // Popup blocked - fallback to new tab
            window.open(url, '_blank');
        } else {
            // Focus the popup
            popup.focus();
        }
    }

    async trackShare() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/share/track`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.shareData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Show feedback if container is available
            const container = document.querySelector(
                `[data-content-type="${this.shareData.content_type}"][data-content-id="${this.shareData.content_id}"]`
            );
            
            if (container && result.coin_awarded) {
                this.showFeedback(
                    container, 
                    `Share tracked! You earned ${result.coin_amount} coin. ${result.remaining_coin_shares} more coins available today.`,
                    'success'
                );
            }

            return result;
        } catch (error) {
            console.error('Error tracking share:', error);
            throw error;
        }
    }

    generateSharedText(button) {
        const title = button.dataset.title || document.title;
        const description = button.dataset.description || '';
        const hashtags = button.dataset.hashtags || '';
        
        let text = title;
        if (description) {
            text += ` - ${description}`;
        }
        if (hashtags) {
            text += ` ${hashtags}`;
        }
        
        return text;
    }

    showFeedback(container, message, type = 'success') {
        const feedbackDiv = container.querySelector('.social-sharing-feedback');
        const alertDiv = feedbackDiv.querySelector('.alert');
        const messageSpan = feedbackDiv.querySelector('.feedback-message');
        
        if (!feedbackDiv || !alertDiv || !messageSpan) {
            console.log(message); // Fallback to console
            return;
        }

        // Update message
        messageSpan.textContent = message;
        
        // Update alert class
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'}`;
        
        // Show feedback
        feedbackDiv.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            feedbackDiv.style.display = 'none';
        }, 5000);
    }

    // Public method to get sharing stats
    async getDailyStats(date = null) {
        try {
            const params = date ? `?target_date=${date}` : '';
            const response = await fetch(`${this.apiBaseUrl}/share/stats/daily${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting daily stats:', error);
            return null;
        }
    }

    // Public method to get analytics
    async getAnalytics(startDate = null, endDate = null) {
        try {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            const queryString = params.toString();
            const url = `${this.apiBaseUrl}/share/analytics${queryString ? '?' + queryString : ''}`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting analytics:', error);
            return null;
        }
    }

    // Public method to get supported platforms
    async getSupportedPlatforms() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/share/platforms`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting supported platforms:', error);
            return null;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.socialSharingManager = new SocialSharingManager();
});

// Expose for manual initialization if needed
window.SocialSharingManager = SocialSharingManager;
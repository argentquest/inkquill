// Referral Tracking System
// This script detects referral parameters in URLs and tracks them

(function() {
    'use strict';

    // Configuration
    const REFERRAL_PARAM = 'ref';
    const REFERRAL_COOKIE = 'ref_code';
    const TRACKING_API_ENDPOINT = '/api/v1/referrals/track';
    
    // Initialize referral tracking when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Always check for referral parameters, even before cookie consent
        detectAndStoreReferral();
        trackReferral();
    });

    /**
     * Detect and store referral in sessionStorage (before cookie consent)
     */
    function detectAndStoreReferral() {
        const urlParams = new URLSearchParams(window.location.search);
        const refCode = urlParams.get(REFERRAL_PARAM);
        
        if (refCode) {
            console.log('Referral parameter detected, storing for later:', refCode);
            // Store in sessionStorage (doesn't require cookie consent)
            sessionStorage.setItem('pending_referral', refCode);
            
            // Clean up URL immediately
            cleanUpUrl();
        }
    }

    /**
     * Main function to detect and track referrals
     */
    async function trackReferral() {
        try {
            // Get referral code from URL parameters OR sessionStorage
            const urlParams = new URLSearchParams(window.location.search);
            let refCode = urlParams.get(REFERRAL_PARAM);
            
            // If no URL parameter, check sessionStorage for pending referral
            if (!refCode) {
                refCode = sessionStorage.getItem('pending_referral');
                if (refCode) {
                    console.log('🔍 JS DEBUG: Using stored referral code:', refCode);
                }
            }
            
            // If still no referral code, check if middleware has set a cookie
            if (!refCode) {
                refCode = getCookie('ref_code');
                if (refCode) {
                    console.log('🔍 JS DEBUG: Found referral cookie set by middleware:', refCode);
                    // Check if we already processed this referral
                    const processedKey = `processed_ref_${refCode}`;
                    if (localStorage.getItem(processedKey)) {
                        console.log('🔍 JS DEBUG: Referral already processed, skipping');
                        return;
                    }
                }
            }
            
            if (!refCode) {
                console.log('🔍 JS DEBUG: No referral parameter detected');
                return;
            }
            
            console.log('Processing referral code:', refCode);
            
            // Check if we already have this referral code in a cookie
            const existingRefCode = getCookie(REFERRAL_COOKIE);
            if (existingRefCode === refCode) {
                console.log('Referral already tracked for this session');
                return;
            }
            
            // Track the referral visit
            await sendReferralTracking(refCode);
            
            // Store in cookie for session persistence
            setCookie(REFERRAL_COOKIE, refCode, 30); // 30 days
            
            // Clear sessionStorage since we've successfully tracked
            sessionStorage.removeItem('pending_referral');
            
            // Mark this referral as processed to avoid double-processing
            const processedKey = `processed_ref_${refCode}`;
            localStorage.setItem(processedKey, 'true');
            
            // Clean up URL (remove ref parameter) without page reload
            cleanUpUrl();
            
        } catch (error) {
            console.error('Error tracking referral:', error);
        }
    }
    
    /**
     * Send referral tracking data to the API
     */
    async function sendReferralTracking(refCode) {
        try {
            console.log('🔍 JS DEBUG: Starting sendReferralTracking');
            console.log('🔍 JS DEBUG: refCode:', refCode);
            console.log('🔍 JS DEBUG: current URL:', window.location.href);
            
            const trackingData = {
                referral_code: refCode,
                landing_page: window.location.pathname + window.location.search + window.location.hash,
                referrer_url: document.referrer || null,
                user_agent: navigator.userAgent,
                screen_resolution: `${window.screen.width}x${window.screen.height}`,
                viewport_size: `${window.innerWidth}x${window.innerHeight}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            };
            
            console.log('🔍 JS DEBUG: trackingData:', JSON.stringify(trackingData, null, 2));
            console.log('🔍 JS DEBUG: Sending request to:', TRACKING_API_ENDPOINT);
            
            const response = await fetch(TRACKING_API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(trackingData)
            });
            
            console.log('🔍 JS DEBUG: Response status:', response.status);
            console.log('🔍 JS DEBUG: Response ok:', response.ok);
            console.log('🔍 JS DEBUG: Response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('🔍 JS DEBUG: Error response body:', errorText);
                
                // Don't throw on 4xx errors, just log them
                if (response.status >= 400 && response.status < 500) {
                    console.warn('🔍 JS DEBUG: Referral tracking returned status:', response.status);
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }
            
            const result = await response.json();
            console.log('🔍 JS DEBUG: Referral tracked successfully:', JSON.stringify(result, null, 2));
            
            // Show success message if reward was given
            if (result.reward_given && window.showToast) {
                console.log('🔍 JS DEBUG: Showing success toast for reward');
                window.showToast(`Welcome! You've earned ${result.reward_amount} coins for visiting through a referral link!`, 'success');
            } else {
                console.log('🔍 JS DEBUG: No reward given or showToast not available');
            }
            
        } catch (error) {
            console.error('🔍 JS DEBUG: Failed to track referral:', error);
            console.error('🔍 JS DEBUG: Error stack:', error.stack);
            // Don't show error to user - fail silently
        }
    }
    
    /**
     * Clean up URL by removing the ref parameter
     */
    function cleanUpUrl() {
        const url = new URL(window.location);
        url.searchParams.delete(REFERRAL_PARAM);
        
        // Use replaceState to update URL without reload
        if (window.history && window.history.replaceState) {
            const newUrl = url.pathname + (url.search ? url.search : '') + url.hash;
            window.history.replaceState({}, document.title, newUrl);
        }
    }
    
    /**
     * Get cookie value by name
     */
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }
    
    /**
     * Set cookie with expiration
     */
    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
    }
    
    // Function to call after cookie consent is given
    function processPendingReferral() {
        const pendingReferral = sessionStorage.getItem('pending_referral');
        if (pendingReferral) {
            console.log('Processing pending referral after cookie consent:', pendingReferral);
            trackReferral();
        }
    }

    // Expose functions to global scope for testing
    window.referralTracking = {
        trackReferral: trackReferral,
        sendReferralTracking: sendReferralTracking,
        processPendingReferral: processPendingReferral
    };
    
})();
// /ai_rag_story_app/app/static/js/main.js

/**
 * main.js
 * -------
 * This file is intended for site-wide JavaScript that applies to multiple pages
 * or general UI enhancements.
 *
 * Examples:
 * - Initializing global Bootstrap components (like tooltips or popovers if used).
 * - Handling a mobile navigation toggle if not fully covered by Bootstrap's default.
 * - Any other general utility functions needed across the site.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Main JavaScript file (main.js) loaded.");

    // Example: Initialize all Bootstrap tooltips on the page
    // This requires that elements have `data-bs-toggle="tooltip"` and a `title` attribute.
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Example: Initialize all Bootstrap popovers on the page
    // This requires `data-bs-toggle="popover"`.
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Setup global authentication error interceptor
    setupGlobalAuthenticationHandler();
    
    // Setup cookie consent management
    setupCookieConsent();
    
    // Setup page engagement tracking
    setupPageEngagementTracking();

    // Add any other global JavaScript initializations or functions here.
    // For example, if you had a theme switcher or a global search bar handler.

    // If there were any `alert()` calls here for general purposes,
    // they should be replaced with `showToast()` from notifications.js.
    // e.g., if (someGlobalCondition) { showToast("Site-wide notification!", "info"); }

    // Check if we just logged out (URL parameter or localStorage flag)
    const urlParams = new URLSearchParams(window.location.search);
    const loggedOut = urlParams.get('logged_out') === 'true' || localStorage.getItem('just_logged_out') === 'true';
    
    if (loggedOut) {
        console.log("User just logged out - clearing balance cache and forcing refresh");
        // Clear any balance caching flags
        localStorage.removeItem('just_logged_out');
        // Force a fresh balance load with cache busting
        setTimeout(() => {
            loadUserCoinBalance(true); // Force refresh with cache busting
        }, 100); // Small delay to ensure cookies are cleared
    } else {
        // Normal balance load
        console.log("Attempting to load user coin balance...");
        loadUserCoinBalance();
    }
    
    // Load AI cost summary for authenticated users
    loadAICostSummary();
});

// Function to load and display user's Coin balance
async function loadUserCoinBalance(forceRefresh = false) {
    const balanceBadge = document.getElementById('coin-balance-badge');
    if (!balanceBadge) {
        console.log("Balance badge element not found");
        return; // Element not found
    }
    
    console.log("Balance badge found, fetching balance...");
    try {
        // Add cache-busting parameter if force refresh is requested
        const cacheBuster = forceRefresh ? `?t=${Date.now()}` : '';
        
        // Try authenticated user balance first
        let response = await fetch(`/api/v1/billing/balance${cacheBuster}`);
        console.log("Authenticated balance API response status:", response.status);
        
        if (response.ok) {
            // Authenticated user
            const data = await response.json();
            console.log("Authenticated balance data received:", data);
            balanceBadge.textContent = `${Math.floor(data.balance)} Coins`;
            updateBalanceBadgeColor(balanceBadge, data.balance);
        } else if (response.status === 401) {
            // Try anonymous user balance
            console.log("User not authenticated, trying anonymous balance...");
            response = await fetch(`/api/v1/public/user/balance${cacheBuster}`);
            console.log("Anonymous balance API response status:", response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log("Anonymous balance data received:", data);
                balanceBadge.textContent = `${Math.floor(data.balance)} Coins`;
                updateBalanceBadgeColor(balanceBadge, data.balance);
            } else {
                // No anonymous user or error - likely cleared cookies
                balanceBadge.textContent = '0 Coins';
                balanceBadge.classList.remove('bg-primary', 'bg-warning');
                balanceBadge.classList.add('bg-danger');
                
                // Check if user previously had an anonymous session and show warning
                checkAndShowCookieWarning();
            }
        } else {
            balanceBadge.textContent = 'Error';
            balanceBadge.classList.add('bg-danger');
        }
    } catch (error) {
        console.error('Error loading coin balance:', error);
        balanceBadge.textContent = 'Error';
        balanceBadge.classList.remove('bg-primary', 'bg-warning');
        balanceBadge.classList.add('bg-danger');
    }
}

// Helper function to update badge color based on balance
function updateBalanceBadgeColor(badge, balance) {
    badge.classList.remove('bg-primary', 'bg-warning', 'bg-danger');
    if (balance < 500) {
        badge.classList.add('bg-danger');
    } else if (balance < 1500) {
        badge.classList.add('bg-warning');
    } else {
        badge.classList.add('bg-primary');
    }
}

// Function to refresh balance (can be called from other scripts after AI usage)
function refreshCoinBalance() {
    console.log("Refreshing coin balance...");
    loadUserCoinBalance();
}

// Make the function available globally for other scripts
window.refreshCoinBalance = refreshCoinBalance;

// Cookie warning functionality
function checkAndShowCookieWarning() {
    // Check if user has visited before (localStorage persists even if cookies are cleared)
    const hasVisitedBefore = localStorage.getItem('rag_app_visited');
    const warningShownToday = localStorage.getItem('cookie_warning_shown_today');
    const today = new Date().toDateString();
    
    // Only show warning if:
    // 1. User has visited before (suggests they had a session)
    // 2. Warning hasn't been shown today
    // 3. Not on login/register pages (to avoid bothering new users)
    const currentPath = window.location.pathname;
    const isAuthPage = currentPath.includes('/login') || currentPath.includes('/register');
    
    if (hasVisitedBefore && warningShownToday !== today && !isAuthPage) {
        console.log("Showing cookie warning modal - user likely cleared cookies");
        showCookieWarningModal();
        // Mark warning as shown today
        localStorage.setItem('cookie_warning_shown_today', today);
    }
    
    // Mark that user has visited (for future sessions)
    if (!hasVisitedBefore) {
        localStorage.setItem('rag_app_visited', 'true');
    }
}

function showCookieWarningModal() {
    const modal = document.getElementById('cookieWarningModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Log event for debugging
        console.log("Cookie warning modal displayed");
        
        // Optional: Add click tracking
        const registerButton = modal.querySelector('a[href="/ui/register"]');
        if (registerButton) {
            registerButton.addEventListener('click', () => {
                console.log("User clicked 'Create Free Account' from cookie warning");
            });
        }
    } else {
        console.error("Cookie warning modal element not found");
    }
}

// AI Cost Summary functionality
async function loadAICostSummary() {
    const lastAiCallInfo = document.getElementById('lastAiCallInfo');
    if (!lastAiCallInfo) {
        console.log("Last AI call info element not found (likely anonymous user)");
        return;
    }
    
    try {
        const response = await fetch('/api/v1/billing/ai-costs/last');
        console.log("Last AI call API response status:", response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log("Last AI call data received:", data);
            updateLastAICallDisplay(data);
            lastAiCallInfo.style.display = 'block';
        } else if (response.status === 401) {
            console.log("User not authenticated - hiding AI call info");
            lastAiCallInfo.style.display = 'none';
        } else {
            console.error("Error loading last AI call data:", response.statusText);
            lastAiCallInfo.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading AI cost summary:', error);
        lastAiCallInfo.style.display = 'none';
    }
}

function updateLastAICallDisplay(data) {
    // Update the new single-line format: "Last AI Call - 0.05 Coin - Story Generation - 08:14"
    const lastAiCallSummary = document.getElementById('lastAiCallSummary');
    
    if (!lastAiCallSummary) {
        return;
    }
    
    if (data.last_call) {
        const cost = Math.floor(data.last_call_cost_coins);
        const callType = formatCallType(data.last_call.call_type);
        const timeAgo = formatTimeAgo(new Date(data.last_call.created_at));
        
        lastAiCallSummary.textContent = `Last AI Call - ${cost} Coins - ${callType} - ${timeAgo}`;
    } else {
        lastAiCallSummary.textContent = 'Last AI Call - 0 Coins - No recent calls - --:--';
    }
}

function formatCallType(callType) {
    // Convert call_type to user-friendly format
    const typeMap = {
        'act_generation': 'Act Writing',
        'scene_generation': 'Scene Writing',
        'act_review': 'Act Review',
        'scene_narrative_generation': 'Scene Generation',
        'scene_metadata_generation': 'Scene Metadata',
        'world_import_from_book': 'World Import',
        'world_import_from_document': 'Document Import',
        'rag_text_generation_character': 'Character RAG',
        'rag_text_generation_location': 'Location RAG',
        'rag_text_generation_lore_item': 'Lore RAG',
        'world_chat': 'World Chat'
    };
    
    return typeMap[callType] || callType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours}h ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days}d ago`;
    }
}

function formatTokenCount(tokens) {
    if (tokens >= 1000000) {
        return `${(tokens / 1000000).toFixed(1)}M tokens`;
    } else if (tokens >= 1000) {
        return `${(tokens / 1000).toFixed(1)}K tokens`;
    }
    return `${tokens} tokens`;
}

// Function to refresh AI cost summary (can be called after AI operations)
function refreshAICostSummary() {
    console.log("Refreshing AI cost summary...");
    loadAICostSummary();
}

// Global function to show insufficient balance modal
function showInsufficientBalanceModal(currentBalance = 0, requiredAmount = 300) {
    // Create modal HTML if it doesn't exist
    let modal = document.getElementById('insufficientBalanceModal');
    if (!modal) {
        const modalHTML = `
            <div class="modal fade" id="insufficientBalanceModal" tabindex="-1" aria-labelledby="insufficientBalanceModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title" id="insufficientBalanceModalLabel">
                                <i class="fas fa-coins me-2"></i>Insufficient Credits
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-exclamation-circle text-warning fa-3x mb-3"></i>
                                <h4>Not Enough Coins!</h4>
                                <p class="mb-3">You need at least <strong><span id="required-amount">300</span> coins</strong> to perform this action.</p>
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle me-2"></i>
                                    <strong>Your current balance:</strong> <span id="modal-balance">0.00</span> Coins
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="fas fa-user-plus text-primary fa-2x mb-2"></i>
                                            <h6>Get Unlimited Access</h6>
                                            <p class="small text-muted mb-2">Register for free and never worry about credits again!</p>
                                            <a href="/register" class="btn btn-primary btn-sm" id="register-link">
                                                <i class="fas fa-user-plus me-1"></i>Register Free
                                            </a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="fas fa-clock text-success fa-2x mb-2"></i>
                                            <h6>Wait for Refresh</h6>
                                            <p class="small text-muted mb-2">Anonymous users get 5 fresh coins weekly</p>
                                            <button class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">
                                                <i class="fas fa-times me-1"></i>Maybe Later
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('insufficientBalanceModal');
    }
    
    // Update balance and required amount in modal
    const modalBalance = modal.querySelector('#modal-balance');
    const requiredAmountSpan = modal.querySelector('#required-amount');
    
    if (modalBalance) {
        modalBalance.textContent = currentBalance.toFixed(2);
    }
    if (requiredAmountSpan) {
        requiredAmountSpan.textContent = requiredAmount;
    }
    
    // Show the modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Helper function to handle API responses that indicate insufficient balance or rate limiting
function handleInsufficientBalanceResponse(response, data) {
    if (response.status === 402 || (data && data.error === 'insufficient_credits')) {
        const currentBalance = data.remaining_balance || 0;
        const requiredBalance = data.required_balance || 3;
        window.showInsufficientBalanceModal(currentBalance, requiredBalance);
        return true; // Indicates that insufficient balance was handled
    }
    
    // Handle 429 Too Many Requests (anonymous user limits exceeded)
    if (response.status === 429) {
        showRateLimitModal(data);
        return true; // Indicates that rate limit was handled
    }
    
    return false; // No balance/rate limit error detected
}

// Function to show rate limit modal for anonymous user creation limits
function showRateLimitModal(data) {
    // Create modal HTML if it doesn't exist
    let modal = document.getElementById('rateLimitModal');
    if (!modal) {
        const modalHTML = `
            <div class="modal fade" id="rateLimitModal" tabindex="-1" aria-labelledby="rateLimitModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title" id="rateLimitModalLabel">
                                <i class="fas fa-exclamation-triangle me-2"></i>Too Many Sessions
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-user-clock text-danger fa-3x mb-3"></i>
                                <h4>Anonymous Session Limit Reached</h4>
                                <p class="mb-3">You've created too many anonymous sessions from this device recently.</p>
                                <div class="alert alert-warning">
                                    <i class="fas fa-info-circle me-2"></i>
                                    <strong>This is to prevent abuse.</strong> Please try again later or register for unlimited access.
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="fas fa-user-plus text-primary fa-2x mb-2"></i>
                                            <h6>Register for Free</h6>
                                            <p class="small text-muted mb-2">Get unlimited access with no session limits!</p>
                                            <a href="/register" class="btn btn-primary btn-sm">
                                                <i class="fas fa-user-plus me-1"></i>Register Now
                                            </a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="fas fa-clock text-warning fa-2x mb-2"></i>
                                            <h6>Try Again Later</h6>
                                            <p class="small text-muted mb-2">Anonymous limits reset after 24 hours</p>
                                            <button class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">
                                                <i class="fas fa-times me-1"></i>Close
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('rateLimitModal');
    }
    
    // Show the modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Helper function for making API calls with automatic balance error handling
async function makeAPICallWithBalanceCheck(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            // Try to parse error response
            let errorData = null;
            try {
                errorData = await response.json();
            } catch (e) {
                // Response might not be JSON
            }
            
            // Check if it's an insufficient balance error
            if (handleInsufficientBalanceResponse(response, errorData)) {
                return { success: false, balanceError: true, data: errorData };
            }
            
            // Other error - rethrow
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        return { success: true, data: data };
        
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

// Generic error handler for balance loading that handles 429 errors
async function loadBalanceWithErrorHandling(apiUrl) {
    try {
        const response = await fetch(apiUrl);
        
        if (response.status === 429) {
            let errorData = null;
            try {
                errorData = await response.json();
            } catch (e) {
                // Response might not be JSON
            }
            showRateLimitModal(errorData);
            return { success: false, rateLimited: true };
        }
        
        if (!response.ok) {
            throw new Error(`Failed to load balance: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data: data };
        
    } catch (error) {
        console.error('Balance loading error:', error);
        return { success: false, error: error };
    }
}

// ========================================================================
// HELP MODAL FUNCTIONALITY
// ========================================================================

// Help Modal Functions
function openHelpModal(pageType) {
    const modal = document.getElementById('helpModal');
    const frame = document.getElementById('helpFrame');
    const title = document.getElementById('helpModalTitle');
    
    // Track help system usage
    if (window.trackFeatureUse) {
        window.trackFeatureUse('help_system', `help_opened_${pageType || 'unknown'}`);
    }
    
    // Map page types to help files and titles
    const helpPages = {
        'world_list': { file: 'world_list.html', title: 'World List Quick Start' },
        'world_detail': { file: 'world_detail.html', title: 'World Detail Quick Start' },
        'world_hierarchy': { file: 'world_hierarchy.html', title: 'World Hierarchy Quick Start' },
        'story_detail': { file: 'story_detail.html', title: 'Story Detail Quick Start' },
        'act_editor': { file: 'act_editor_ui.html', title: 'Act Editor Quick Start' },
        'scene_editor': { file: 'scene_editor_ui.html', title: 'Scene Editor Quick Start' },
        'character_detail': { file: 'character_detail.html', title: 'Character Detail Quick Start' },
        'location_detail': { file: 'location_detail.html', title: 'Location Detail Quick Start' },
        'lore_item_detail': { file: 'lore_item_detail.html', title: 'Lore Item Quick Start' },
        'billing': { file: 'billing_dashboard.html', title: 'Billing Quick Start' },
        'register': { file: 'register.html', title: 'Registration Quick Start' },
        'forum': { file: 'forum_home.html', title: 'Forum Quick Start' },
        'act_review': { file: 'act_ai_review.html', title: 'AI Review Quick Start' },
        'documents': { file: 'document_manager.html', title: 'Document Manager Quick Start' },
        'prompts': { file: 'prompts.html', title: 'Prompts Quick Start' },
        'admin': { file: 'index.html', title: 'Admin Quick Start' },
        'my_account': { file: 'index.html', title: 'My Account Quick Start' }
    };
    
    const helpInfo = helpPages[pageType] || { file: 'index.html', title: 'General Quick Start' };
    
    frame.src = `/static/help/${helpInfo.file}`;
    title.textContent = helpInfo.title;
    modal.style.display = 'block';
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
}

function closeHelpModal() {
    const modal = document.getElementById('helpModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('helpModal');
    if (event.target === modal) {
        closeHelpModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.getElementById('helpModal');
        if (modal && modal.style.display === 'block') {
            closeHelpModal();
        }
    }
});

// ========================================================================
// GLOBAL AUTHENTICATION ERROR HANDLING
// ========================================================================

// Setup global authentication error interceptor
function setupGlobalAuthenticationHandler() {
    // Intercept clicks on links that might require authentication
    document.addEventListener('click', function(event) {
        const target = event.target.closest('a[href]');
        if (!target) return;
        
        const href = target.getAttribute('href');
        
        // Skip if it's an external link, anchor link, or javascript link
        if (!href || href.startsWith('#') || href.startsWith('javascript:') || 
            href.startsWith('http://') || href.startsWith('https://') ||
            href.startsWith('mailto:') || href.startsWith('tel:')) {
            return;
        }
        
        // Skip if it's already a login/register/public page
        if (href.includes('/login') || href.includes('/register') || 
            href.includes('/ui/') === false || href === '/') {
            return;
        }
        
        // For protected routes, intercept and check authentication
        if (isProtectedRoute(href)) {
            event.preventDefault();
            handleProtectedRouteClick(href);
        }
    });
}

// Check if a route likely requires authentication based on patterns
function isProtectedRoute(href) {
    const protectedPatterns = [
        '/ui/stories',
        '/ui/worlds', 
        '/ui/characters',
        '/ui/locations',
        '/ui/lore-items',
        '/ui/acts',
        '/ui/scenes',
        '/ui/prompts',
        '/ui/documents',
        '/ui/billing',
        '/ui/my-account',
        '/ui/admin'
    ];
    
    return protectedPatterns.some(pattern => href.includes(pattern));
}

// Handle clicks on protected routes for unauthenticated users
async function handleProtectedRouteClick(href) {
    try {
        // Try a lightweight API call to check authentication status
        const response = await fetch('/api/v1/auth/ws-ticket', {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            // User is authenticated, allow navigation
            window.location.href = href;
        } else if (response.status === 401) {
            // User is not authenticated, show modal
            showAuthRequiredModal();
        } else {
            // Other error, allow navigation (might be server issue)
            window.location.href = href;
        }
    } catch (error) {
        console.error('Error checking authentication:', error);
        // On error, allow navigation
        window.location.href = href;
    }
}

// Show the authentication required modal
function showAuthRequiredModal() {
    const modal = document.getElementById('authRequiredModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        console.log("Authentication required modal displayed");
    } else {
        console.error("Authentication required modal element not found");
        // Fallback: redirect to login
        window.location.href = '/ui/login';
    }
}

// Enhanced handleInsufficientBalanceResponse to also handle auth errors
function handleAPIResponse(response, data) {
    // Handle authentication errors
    if (response.status === 401 && data && data.detail === 'Could not validate credentials') {
        showAuthRequiredModal();
        return true;
    }
    
    // Handle balance/rate limit errors (existing functionality)
    return handleInsufficientBalanceResponse(response, data);
}

// ========================================================================
// COOKIE CONSENT MANAGEMENT
// ========================================================================

// Setup cookie consent functionality
function setupCookieConsent() {
    // Check if consent has already been given
    const consentGiven = localStorage.getItem('cookie_consent_given');
    const analyticsConsent = localStorage.getItem('analytics_consent');
    
    // Show banner if no consent has been recorded
    if (!consentGiven) {
        setTimeout(() => {
            showCookieConsentBanner();
        }, 1000); // Delay to not interfere with page load
    }
    
    // Update analytics toggle in modal based on saved preference
    const analyticsToggle = document.getElementById('analyticsCookies');
    if (analyticsToggle) {
        analyticsToggle.checked = analyticsConsent === 'granted';
        
        // Add event listener for toggle changes
        analyticsToggle.addEventListener('change', function() {
            if (this.checked) {
                console.log('Analytics cookies enabled via toggle');
            } else {
                console.log('Analytics cookies disabled via toggle');
            }
        });
    }
}

// Show the cookie consent banner
function showCookieConsentBanner() {
    const banner = document.getElementById('cookieConsentBanner');
    if (banner) {
        banner.style.display = 'block';
        // Add entrance animation
        setTimeout(() => {
            banner.style.opacity = '1';
            banner.style.transform = 'translateY(0)';
        }, 100);
    }
}

// Hide the cookie consent banner
function hideCookieConsentBanner() {
    const banner = document.getElementById('cookieConsentBanner');
    if (banner) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(100%)';
        setTimeout(() => {
            banner.style.display = 'none';
        }, 300);
    }
}

// Handle cookie consent choices
function handleCookieChoice(choice) {
    console.log('Cookie choice:', choice);
    
    // Mark that consent has been given
    localStorage.setItem('cookie_consent_given', 'true');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    
    let analyticsEnabled = false;
    
    switch (choice) {
        case 'all':
            analyticsEnabled = true;
            localStorage.setItem('cookie_consent_level', 'all');
            break;
        case 'necessary':
            analyticsEnabled = false;
            localStorage.setItem('cookie_consent_level', 'necessary');
            break;
        case 'custom':
            // Check the analytics toggle
            const analyticsToggle = document.getElementById('analyticsCookies');
            analyticsEnabled = analyticsToggle ? analyticsToggle.checked : false;
            localStorage.setItem('cookie_consent_level', 'custom');
            break;
    }
    
    // Update analytics consent
    if (analyticsEnabled) {
        if (window.grantAnalyticsConsent) {
            window.grantAnalyticsConsent();
        }
    } else {
        if (window.denyAnalyticsConsent) {
            window.denyAnalyticsConsent();
        }
    }
    
    // Hide the banner
    hideCookieConsentBanner();
    
    // Process any pending referral tracking now that cookies are accepted
    if (window.referralTracking && window.referralTracking.processPendingReferral) {
        window.referralTracking.processPendingReferral();
    }
    
    // Show confirmation toast
    if (typeof showToast !== 'undefined') {
        const message = analyticsEnabled ? 
            'Cookie preferences saved. Analytics enabled.' : 
            'Cookie preferences saved. Analytics disabled.';
        showToast(message, 'success');
    }
    
    console.log('Cookie consent processed:', {
        choice: choice,
        analyticsEnabled: analyticsEnabled,
        timestamp: new Date().toISOString()
    });
}

// Show cookie preferences modal (for footer link)
function showCookiePreferences() {
    // Update the modal toggle to reflect current settings
    const analyticsToggle = document.getElementById('analyticsCookies');
    const currentConsent = localStorage.getItem('analytics_consent');
    
    if (analyticsToggle) {
        analyticsToggle.checked = currentConsent === 'granted';
    }
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('cookieDetailsModal'));
    modal.show();
}

// Reset cookie consent (for testing or user request)
function resetCookieConsent() {
    localStorage.removeItem('cookie_consent_given');
    localStorage.removeItem('cookie_consent_date');
    localStorage.removeItem('cookie_consent_level');
    localStorage.removeItem('analytics_consent');
    
    // Deny analytics consent
    if (window.denyAnalyticsConsent) {
        window.denyAnalyticsConsent();
    }
    
    // Show banner again
    showCookieConsentBanner();
    
    console.log('Cookie consent reset');
}

// Get current consent status (utility function)
function getCookieConsentStatus() {
    return {
        consentGiven: localStorage.getItem('cookie_consent_given') === 'true',
        consentLevel: localStorage.getItem('cookie_consent_level'),
        analyticsConsent: localStorage.getItem('analytics_consent'),
        consentDate: localStorage.getItem('cookie_consent_date')
    };
}

// ========================================================================
// PAGE ENGAGEMENT TRACKING
// ========================================================================

// Track page engagement metrics
function setupPageEngagementTracking() {
    // Track navigation to key pages
    trackPageNavigation();
    
    // Track button clicks on important elements
    trackImportantButtonClicks();
    
    // Track form interactions
    trackFormEngagement();
    
    // Track time spent on page
    trackPageTimeSpent();
}

function trackPageNavigation() {
    // Track which page type user is on
    const path = window.location.pathname;
    let pageType = 'unknown';
    
    if (path === '/' || path === '/ui/' || path === '/ui') {
        pageType = 'home';
    } else if (path.includes('/worlds')) {
        pageType = 'worlds';
    } else if (path.includes('/stories')) {
        pageType = 'stories';
    } else if (path.includes('/acts')) {
        pageType = 'acts';
    } else if (path.includes('/scenes')) {
        pageType = 'scenes';
    } else if (path.includes('/characters')) {
        pageType = 'characters';
    } else if (path.includes('/locations')) {
        pageType = 'locations';
    } else if (path.includes('/lore')) {
        pageType = 'lore';
    } else if (path.includes('/documents')) {
        pageType = 'documents';
    } else if (path.includes('/prompts')) {
        pageType = 'prompts';
    } else if (path.includes('/admin')) {
        pageType = 'admin';
    } else if (path.includes('/login')) {
        pageType = 'login';
    } else if (path.includes('/register')) {
        pageType = 'register';
    } else if (path.includes('/world-chat')) {
        pageType = 'world_chat';
    } else if (path.includes('/billing')) {
        pageType = 'billing';
    }
    
    // Track page view with feature use
    if (window.trackFeatureUse) {
        window.trackFeatureUse('page_navigation', pageType);
    }
}

function trackImportantButtonClicks() {
    // Track clicks on create/add buttons
    document.addEventListener('click', function(event) {
        const target = event.target.closest('button, a');
        if (!target) return;
        
        const buttonText = target.textContent?.toLowerCase() || '';
        const buttonClass = target.className || '';
        const buttonId = target.id || '';
        
        // Track create/add actions
        if (buttonText.includes('create') || buttonText.includes('add') || buttonText.includes('new')) {
            let featureType = 'general_create';
            
            if (buttonText.includes('world') || buttonId.includes('world')) {
                featureType = 'world_create';
            } else if (buttonText.includes('story') || buttonId.includes('story')) {
                featureType = 'story_create';
            } else if (buttonText.includes('character') || buttonId.includes('character')) {
                featureType = 'character_create';
            } else if (buttonText.includes('location') || buttonId.includes('location')) {
                featureType = 'location_create';
            } else if (buttonText.includes('scene') || buttonId.includes('scene')) {
                featureType = 'scene_create';
            } else if (buttonText.includes('act') || buttonId.includes('act')) {
                featureType = 'act_create';
            }
            
            if (window.trackFeatureUse) {
                window.trackFeatureUse(featureType, 'button_click');
            }
        }
        
        // Track edit actions
        if (buttonText.includes('edit') || buttonClass.includes('edit')) {
            if (window.trackFeatureUse) {
                window.trackFeatureUse('content_edit', 'button_click');
            }
        }
        
        // Track delete actions
        if (buttonText.includes('delete') || buttonClass.includes('delete') || buttonClass.includes('danger')) {
            if (window.trackFeatureUse) {
                window.trackFeatureUse('content_delete', 'button_click');
            }
        }
        
        // Track save actions
        if (buttonText.includes('save') || buttonId.includes('save')) {
            if (window.trackFeatureUse) {
                window.trackFeatureUse('content_save', 'button_click');
            }
        }
    });
}

function trackFormEngagement() {
    // Track form submissions
    document.addEventListener('submit', function(event) {
        const form = event.target;
        const formId = form.id || '';
        const formAction = form.action || '';
        
        let formType = 'unknown_form';
        
        if (formId.includes('login') || formAction.includes('login')) {
            formType = 'login_form';
        } else if (formId.includes('register') || formAction.includes('register')) {
            formType = 'register_form';
        } else if (formId.includes('world') || formAction.includes('world')) {
            formType = 'world_form';
        } else if (formId.includes('story') || formAction.includes('story')) {
            formType = 'story_form';
        } else if (formId.includes('character') || formAction.includes('character')) {
            formType = 'character_form';
        } else if (formId.includes('location') || formAction.includes('location')) {
            formType = 'location_form';
        } else if (formId.includes('import') || formAction.includes('import')) {
            formType = 'import_form';
        }
        
        if (window.trackFeatureUse) {
            window.trackFeatureUse('form_submission', formType);
        }
    });
}

function trackPageTimeSpent() {
    let startTime = Date.now();
    let isActive = true;
    let totalActiveTime = 0;
    
    // Track when user becomes active/inactive
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            if (isActive) {
                totalActiveTime += Date.now() - startTime;
                isActive = false;
            }
        } else {
            startTime = Date.now();
            isActive = true;
        }
    });
    
    // Track active time every 30 seconds for engaged users
    setInterval(() => {
        if (isActive) {
            const currentActiveTime = totalActiveTime + (Date.now() - startTime);
            
            // Track engaged users (more than 30 seconds)
            if (currentActiveTime > 30000 && window.trackFeatureUse) {
                const timeCategory = currentActiveTime > 300000 ? 'long_session' : 
                                   currentActiveTime > 120000 ? 'medium_session' : 'short_session';
                window.trackFeatureUse('page_engagement', timeCategory);
            }
        }
    }, 30000);
    
    // Track time on page unload
    window.addEventListener('beforeunload', function() {
        if (isActive) {
            totalActiveTime += Date.now() - startTime;
        }
        
        if (totalActiveTime > 10000 && window.trackFeatureUse) { // More than 10 seconds
            const timeCategory = totalActiveTime > 300000 ? 'long_session' : 
                               totalActiveTime > 120000 ? 'medium_session' : 'short_session';
            window.trackFeatureUse('session_duration', timeCategory);
        }
    });
}

// Make functions available globally for other scripts
window.refreshAICostSummary = refreshAICostSummary;
window.showInsufficientBalanceModal = showInsufficientBalanceModal;
window.showRateLimitModal = showRateLimitModal;
window.handleInsufficientBalanceResponse = handleInsufficientBalanceResponse;
window.makeAPICallWithBalanceCheck = makeAPICallWithBalanceCheck;
window.loadBalanceWithErrorHandling = loadBalanceWithErrorHandling;
window.openHelpModal = openHelpModal;
window.closeHelpModal = closeHelpModal;
window.showAuthRequiredModal = showAuthRequiredModal;
window.handleAPIResponse = handleAPIResponse;
window.handleCookieChoice = handleCookieChoice;
window.showCookiePreferences = showCookiePreferences;
window.resetCookieConsent = resetCookieConsent;
window.getCookieConsentStatus = getCookieConsentStatus;
window.setupPageEngagementTracking = setupPageEngagementTracking;

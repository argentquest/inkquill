// /ai_rag_story_app/app/static/js/sidebar.js

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const userDropdownToggle = document.getElementById('userDropdownToggle');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    const body = document.body;

    // Check for saved sidebar state in localStorage
    const savedState = localStorage.getItem('sidebarExpanded');
    if (sidebar) {
        if (savedState === 'true') {
            expandSidebar();
        } else {
            collapseSidebar();
        }
    }

    // Initialize submenu functionality
    initializeSubmenus();

    function initializeSubmenus() {
        // QuickStart no longer has submenu - removed
        
        // Set up Admin submenu (if it exists)
        const adminMenuItem = document.getElementById('adminMenuItem');
        if (adminMenuItem) {
            setupSubmenu(
                adminMenuItem,
                document.getElementById('adminLink'),
                document.getElementById('adminArrow'),
                'Admin'
            );
        }
    }

    // Toggle sidebar function
    function toggleSidebar() {
        if (body.classList.contains('sidebar-expanded')) {
            collapseSidebar();
        } else {
            expandSidebar();
        }
    }

    // Expand sidebar
    function expandSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('sidebar-collapsed');
        body.classList.add('sidebar-expanded');
        
        // Show overlay on mobile
        if (window.innerWidth <= 991) {
            sidebar.classList.add('mobile-open');
            if (sidebarOverlay) sidebarOverlay.classList.add('active');
        }
        
        // Save state
        localStorage.setItem('sidebarExpanded', 'true');
        
        // Focus management
        sidebar.setAttribute('aria-hidden', 'false');
        
        // Announce to screen readers
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-label', 'Close sidebar');
        }
    }

    // Collapse sidebar
    function collapseSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('sidebar-collapsed');
        body.classList.remove('sidebar-expanded');
        sidebar.classList.remove('mobile-open');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');
        
        // Close user dropdown if open
        if (userDropdownMenu) {
            userDropdownMenu.classList.remove('show');
            if (userDropdownToggle) {
                userDropdownToggle.setAttribute('aria-expanded', 'false');
            }
        }
        
        // Save state
        localStorage.setItem('sidebarExpanded', 'false');
        
        // Focus management
        sidebar.setAttribute('aria-hidden', 'true');
        
        // Announce to screen readers
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-label', 'Open sidebar');
        }
    }

    // Event listeners
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    if (sidebarClose) {
        sidebarClose.addEventListener('click', collapseSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', collapseSidebar);
    }

    // User dropdown functionality
    if (userDropdownToggle && userDropdownMenu) {
        userDropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isExpanded = userDropdownToggle.getAttribute('aria-expanded') === 'true';
            
            if (isExpanded) {
                userDropdownMenu.classList.remove('show');
                userDropdownToggle.setAttribute('aria-expanded', 'false');
            } else {
                userDropdownMenu.classList.add('show');
                userDropdownToggle.setAttribute('aria-expanded', 'true');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userDropdownToggle.contains(e.target) && !userDropdownMenu.contains(e.target)) {
                userDropdownMenu.classList.remove('show');
                userDropdownToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        // ESC key closes sidebar
        if (e.key === 'Escape' && body.classList.contains('sidebar-expanded')) {
            collapseSidebar();
            if (sidebarToggle) {
                sidebarToggle.focus();
            }
        }
        
        // Alt + M toggles sidebar (accessibility shortcut)
        if (e.altKey && e.key.toLowerCase() === 'm') {
            e.preventDefault();
            toggleSidebar();
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        // Auto-expand sidebar on desktop if it was expanded before
        if (window.innerWidth > 991) {
            if (sidebarOverlay) sidebarOverlay.classList.remove('active');
            
            // If sidebar was manually collapsed, respect that choice
            const savedState = localStorage.getItem('sidebarExpanded');
            if (savedState === 'true' && !body.classList.contains('sidebar-expanded')) {
                expandSidebar();
            }
        } else {
            // On mobile, always collapse sidebar when resizing
            if (body.classList.contains('sidebar-expanded')) {
                sidebarOverlay.classList.add('active');
            }
        }
    });

    // Add smooth scroll behavior to navigation links
    if (sidebar) {
        const navLinks = sidebar.querySelectorAll('.nav-link[href^="#"]');
        navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close sidebar on mobile after navigation
                if (window.innerWidth <= 991) {
                    collapseSidebar();
                }
            }
        });
    });
    }

    // Initialize ARIA attributes
    function initializeAria() {
        if (sidebar) {
            sidebar.setAttribute('role', 'navigation');
            sidebar.setAttribute('aria-label', 'Main navigation');
            sidebar.setAttribute('aria-hidden', body.classList.contains('sidebar-expanded') ? 'false' : 'true');
        }
        
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-label', body.classList.contains('sidebar-expanded') ? 'Close sidebar' : 'Open sidebar');
        }
        
        if (userDropdownToggle) {
            userDropdownToggle.setAttribute('aria-expanded', 'false');
            userDropdownToggle.setAttribute('aria-haspopup', 'true');
        }
        
        if (userDropdownMenu) {
            userDropdownMenu.setAttribute('role', 'menu');
        }
    }

    // Initialize accessibility attributes
    initializeAria();

    // Add loading state handling
    function showLoadingState() {
        if (sidebar) {
            const navLinks = sidebar.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.style.pointerEvents = 'none';
                link.style.opacity = '0.6';
            });
        }
    }

    function hideLoadingState() {
        if (sidebar) {
            const navLinks = sidebar.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.style.pointerEvents = '';
                link.style.opacity = '';
            });
        }
    }

    // Expose functions globally for potential external use
    // ========================================================================
    // SUBMENU FUNCTIONALITY (ADMIN ONLY)
    // ========================================================================
    
    const adminMenuItem = document.getElementById('adminMenuItem');
    const adminLink = document.getElementById('adminLink');
    const adminArrow = document.getElementById('adminArrow');
    
    // Function to detect if we're on mobile
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Generic function to setup submenu functionality
    function setupSubmenu(menuItem, menuLink, menuArrow, debugName) {
        if (!menuItem || !menuLink) return;
        
        // Function to toggle submenu
        function toggleSubmenu(e) {
            // Check if arrow was clicked - if so, let the dedicated arrow handler deal with it
            const arrowClicked = e.target === menuArrow || e.target.closest('.submenu-arrow');
            
            if (arrowClicked) {
                // Let the dedicated arrow click handler deal with this
                return;
            }
            
            // Only handle mobile clicks on the main link text
            if (isMobile()) {
                console.log(`${debugName} main link clicked on mobile`);
                e.preventDefault();
                e.stopPropagation();
                
                menuItem.classList.toggle('submenu-open');
                
                // Update aria-expanded attribute for accessibility
                const isExpanded = menuItem.classList.contains('submenu-open');
                menuLink.setAttribute('aria-expanded', isExpanded);
                
                console.log(`${debugName} mobile submenu state:`, isExpanded);
            }
            // On desktop, let the link navigate normally when clicking the text
        }
        
        // Add click event listener
        menuLink.addEventListener('click', toggleSubmenu);
        
        // Add click event specifically for the arrow
        if (menuArrow) {
            menuArrow.addEventListener('click', function(e) {
                console.log(`${debugName} arrow clicked!`);
                console.log(`${debugName} current expanded state before toggle:`, menuItem.classList.contains('submenu-open'));
                
                e.preventDefault();
                e.stopPropagation();
                
                // Check current state before toggling
                const wasExpanded = menuItem.classList.contains('submenu-open');
                
                if (wasExpanded) {
                    menuItem.classList.remove('submenu-open');
                } else {
                    menuItem.classList.add('submenu-open');
                }
                
                const isExpanded = menuItem.classList.contains('submenu-open');
                menuLink.setAttribute('aria-expanded', isExpanded);
                
                console.log(`${debugName} submenu expanded after toggle:`, isExpanded);
                console.log(`${debugName} CSS classes:`, menuItem.className);
            });
            
            // Also add mousedown for better responsiveness
            menuArrow.addEventListener('mousedown', function(e) {
                e.preventDefault();
            });
        }
        
        // Close submenu when clicking outside (mobile)
        document.addEventListener('click', function(e) {
            if (isMobile() && !menuItem.contains(e.target)) {
                menuItem.classList.remove('submenu-open');
                menuLink.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Handle window resize - close submenu on mobile
        window.addEventListener('resize', function() {
            if (isMobile()) {
                menuItem.classList.remove('submenu-open');
                menuLink.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Initialize aria-expanded attribute
        menuLink.setAttribute('aria-expanded', 'false');
    }
    
    // Setup Admin submenu (if it exists)
    if (adminMenuItem) {
        setupSubmenu(adminMenuItem, adminLink, adminArrow, 'Admin');
    }

    window.sidebarController = {
        expand: expandSidebar,
        collapse: collapseSidebar,
        toggle: toggleSidebar,
        showLoading: showLoadingState,
        hideLoading: hideLoadingState
    };

    // Debug mode for development
    if (window.location.search.includes('debug=sidebar')) {
        console.log('Sidebar controller initialized', {
            sidebar: !!sidebar,
            toggle: !!sidebarToggle,
            close: !!sidebarClose,
            overlay: !!sidebarOverlay,
            userDropdown: !!userDropdownToggle,
            admin: !!adminMenuItem,
            savedState: savedState
        });
    }
});
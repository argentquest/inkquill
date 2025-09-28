/* ========================================================================
   THEME TOGGLE FUNCTIONALITY
   Day/Night mode switching with system preference detection and persistence
   ======================================================================== */

class ThemeManager {
  constructor() {
    this.init();
  }

  init() {
    // Initialize theme from storage or system preference
    this.setInitialTheme();
    
    // Set up theme toggle listeners
    this.setupToggleListeners();
    
    // Listen for system theme changes
    this.listenForSystemChanges();
    
    // Update theme toggle UI
    this.updateToggleUI();
  }

  /**
   * Set initial theme - HARDCODED TO LIGHT MODE
   */
  setInitialTheme() {
    // Force light mode - ignore saved preferences and system preference
    this.setTheme('light');
  }

  /**
   * Set the theme - HARDCODED TO LIGHT MODE ONLY
   */
  setTheme(theme) {
    // Force light mode regardless of parameter
    theme = 'light';
    
    // Add transition class to prevent flicker
    document.documentElement.setAttribute('data-theme-changing', '');
    
    // Set theme attribute to light only
    document.documentElement.setAttribute('data-theme', 'light');
    
    // Update meta theme-color for mobile browsers
    this.updateMetaThemeColor('light');
    
    // Save to localStorage as light
    localStorage.setItem('theme', 'light');
    
    // Update toggle UI
    this.updateToggleUI();
    
    // Remove transition class after a brief delay
    setTimeout(() => {
      document.documentElement.removeAttribute('data-theme-changing');
    }, 50);
    
    // Dispatch custom event for other components
    window.dispatchEvent(new CustomEvent('themeChanged', { 
      detail: { theme: 'light' } 
    }));
  }

  /**
   * Toggle between light and dark themes - DISABLED (FORCE LIGHT MODE)
   */
  toggleTheme() {
    // Do nothing - theme switching is disabled
    // Always stay in light mode
    this.setTheme('light');
  }

  /**
   * Get current theme - ALWAYS RETURNS LIGHT
   * @returns {string} Current theme (always 'light')
   */
  getCurrentTheme() {
    return 'light';
  }

  /**
   * Update meta theme-color for mobile browsers
   * @param {string} theme - Current theme
   */
  updateMetaThemeColor(theme) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }
    
    // Set appropriate color based on theme
    const colors = {
      light: '#ffffff',
      dark: '#0f172a'
    };
    
    metaThemeColor.content = colors[theme] || colors.light;
  }

  /**
   * Set up click listeners for theme toggle buttons
   */
  setupToggleListeners() {
    // Find all theme toggle buttons
    const toggleButtons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
    
    toggleButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleTheme();
        
        // Add visual feedback
        this.addClickFeedback(button);
      });
    });
  }

  /**
   * Add visual feedback to toggle button
   * @param {HTMLElement} button - Button element
   */
  addClickFeedback(button) {
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
      button.style.transform = '';
    }, 150);
  }

  /**
   * Update theme toggle UI elements
   */
  updateToggleUI() {
    const currentTheme = this.getCurrentTheme();
    const toggleButtons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
    
    toggleButtons.forEach(button => {
      // Update data attribute
      button.setAttribute('data-theme', currentTheme);
      
      // Update icon if it has theme-specific icons
      const icon = button.querySelector('.theme-toggle-icon, i');
      if (icon) {
        // Remove existing theme classes
        icon.classList.remove('fa-sun', 'fa-moon', 'fa-sun-bright', 'fa-moon-stars');
        
        // Add appropriate icon
        if (currentTheme === 'dark') {
          icon.classList.add('fa-sun');
          button.setAttribute('title', 'Switch to light mode');
          button.setAttribute('aria-label', 'Switch to light mode');
        } else {
          icon.classList.add('fa-moon');
          button.setAttribute('title', 'Switch to dark mode');
          button.setAttribute('aria-label', 'Switch to dark mode');
        }
      }
      
      // Update text if present
      const text = button.querySelector('.theme-toggle-text');
      if (text) {
        text.textContent = currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
      }
    });
  }

  /**
   * Listen for system theme preference changes
   */
  listenForSystemChanges() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    mediaQuery.addEventListener('change', (e) => {
      // Only auto-switch if user hasn't manually set a preference
      const savedTheme = localStorage.getItem('theme');
      
      if (!savedTheme) {
        const newTheme = e.matches ? 'dark' : 'light';
        this.setTheme(newTheme);
      }
    });
  }

  /**
   * Reset theme preference (follow system)
   */
  resetToSystem() {
    localStorage.removeItem('theme');
    this.setInitialTheme();
  }

  /**
   * Get system theme preference
   * @returns {string} System theme preference
   */
  getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  /**
   * Check if theme follows system preference
   * @returns {boolean} True if following system preference
   */
  isFollowingSystem() {
    return !localStorage.getItem('theme');
  }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();
});

// Expose for manual initialization if needed
window.ThemeManager = ThemeManager;

/* ========================================================================
   THEME-AWARE COMPONENTS
   Utilities for components that need to respond to theme changes
   ======================================================================== */

/**
 * Register a callback for theme changes
 * @param {Function} callback - Function to call when theme changes
 */
function onThemeChange(callback) {
  window.addEventListener('themeChanged', callback);
}

/**
 * Get current theme
 * @returns {string} Current theme
 */
function getCurrentTheme() {
  return window.themeManager ? window.themeManager.getCurrentTheme() : 'light';
}

/**
 * Set theme programmatically
 * @param {string} theme - Theme to set
 */
function setTheme(theme) {
  if (window.themeManager) {
    window.themeManager.setTheme(theme);
  }
}

// Export utilities
window.themeUtils = {
  onThemeChange,
  getCurrentTheme,
  setTheme
};

/* ========================================================================
   KEYBOARD SHORTCUTS
   ======================================================================== */

document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + Shift + D to toggle theme - DISABLED
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
    e.preventDefault();
    // Theme switching disabled - do nothing
  }
});

/* ========================================================================
   PRINT STYLES SUPPORT
   ======================================================================== */

// Force light theme for printing
window.addEventListener('beforeprint', () => {
  document.documentElement.setAttribute('data-print-mode', 'true');
  document.documentElement.setAttribute('data-theme', 'light');
});

window.addEventListener('afterprint', () => {
  document.documentElement.removeAttribute('data-print-mode');
  if (window.themeManager) {
    const currentTheme = window.themeManager.getCurrentTheme();
    document.documentElement.setAttribute('data-theme', currentTheme);
  }
});
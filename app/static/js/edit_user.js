// Edit User Page JavaScript

class EditUserManager {
    constructor() {
        this.userId = null;
        this.init();
    }
    
    init() {
        this.extractUserIdFromUrl();
        this.setupEventListeners();
    }
    
    extractUserIdFromUrl() {
        // Extract user ID from URL path like /ui/admin/users/123/edit
        const pathParts = window.location.pathname.split('/');
        const userIdIndex = pathParts.indexOf('users') + 1;
        if (userIdIndex > 0 && userIdIndex < pathParts.length) {
            this.userId = parseInt(pathParts[userIdIndex]);
        }
    }
    
    setupEventListeners() {
        // Form submission
        const editForm = document.getElementById('edit-user-form');
        if (editForm) {
            editForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveUser();
            });
        }
        
        // Toggle user status button
        const toggleBtn = document.getElementById('toggle-user-status');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const userId = parseInt(toggleBtn.dataset.userId);
                const currentStatus = toggleBtn.dataset.currentStatus === 'true';
                this.toggleUserStatus(userId, currentStatus);
            });
        }
        
        // Impersonate user button
        const impersonateBtn = document.getElementById('impersonate-user');
        if (impersonateBtn) {
            impersonateBtn.addEventListener('click', () => {
                const username = impersonateBtn.dataset.username;
                this.impersonateUser(username);
            });
        }
    }
    
    async saveUser() {
        const form = document.getElementById('edit-user-form');
        const formData = new FormData(form);
        
        const userData = {
            email: formData.get('email').trim() || null,
            display_name: formData.get('display_name').trim() || null,
            is_admin: formData.has('is_admin')
        };
        
        // Remove null/empty values
        Object.keys(userData).forEach(key => {
            if (userData[key] === null || userData[key] === '') {
                delete userData[key];
            }
        });
        
        try {
            this.showLoading('save-user-button', 'Saving...');
            
            const response = await fetch(`/api/v1/users/${this.userId}/edit`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update user');
            }
            
            const updatedUser = await response.json();
            
            this.showSuccess('User updated successfully!');
            
            // Update the sidebar information
            this.updateSidebarInfo(updatedUser);
            
        } catch (error) {
            console.error('Error updating user:', error);
            this.showError(`Failed to update user: ${error.message}`);
        } finally {
            this.hideLoading('save-user-button', 'Save Changes');
        }
    }
    
    async toggleUserStatus(userId, currentStatus) {
        const action = currentStatus ? 'deactivate' : 'activate';
        
        if (!confirm(`Are you sure you want to ${action} this user?`)) {
            return;
        }
        
        try {
            const toggleBtn = document.getElementById('toggle-user-status');
            this.showLoading('toggle-user-status', `${action === 'activate' ? 'Activating' : 'Deactivating'}...`);
            
            const response = await fetch(`/api/v1/users/${userId}/toggle-active`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to ${action} user`);
            }
            
            const updatedUser = await response.json();
            
            this.showSuccess(`User successfully ${action}d!`);
            
            // Update the button and sidebar
            this.updateToggleButton(updatedUser.is_active);
            this.updateSidebarInfo(updatedUser);
            
        } catch (error) {
            console.error(`Error ${action}ing user:`, error);
            this.showError(`Failed to ${action} user: ${error.message}`);
        } finally {
            const newText = currentStatus ? 
                '<i class="fas fa-user-check me-1"></i> Activate User' : 
                '<i class="fas fa-user-slash me-1"></i> Deactivate User';
            this.hideLoading('toggle-user-status', newText);
        }
    }
    
    async impersonateUser(username) {
        if (!confirm(`Are you sure you want to impersonate user "${username}"?`)) {
            return;
        }
        
        try {
            this.showLoading('impersonate-user', 'Impersonating...');
            
            const response = await fetch('/api/v1/auth/impersonate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to impersonate user');
            }
            
            const result = await response.json();
            
            this.showSuccess(`Successfully impersonating user "${username}". Redirecting to admin panel...`);
            
            // Redirect to admin users page after a short delay
            setTimeout(() => {
                window.location.href = '/ui/admin/users';
            }, 2000);
            
        } catch (error) {
            console.error('Error impersonating user:', error);
            this.showError(`Failed to impersonate user: ${error.message}`);
        } finally {
            this.hideLoading('impersonate-user', '<i class="fas fa-user-secret me-1"></i> Impersonate User');
        }
    }
    
    updateToggleButton(isActive) {
        const toggleBtn = document.getElementById('toggle-user-status');
        if (!toggleBtn) return;
        
        toggleBtn.dataset.currentStatus = isActive.toString();
        
        if (isActive) {
            toggleBtn.className = 'btn toggle-btn w-100';
            toggleBtn.innerHTML = '<i class="fas fa-user-slash me-1"></i> Deactivate User';
        } else {
            toggleBtn.className = 'btn toggle-btn w-100 inactive';
            toggleBtn.innerHTML = '<i class="fas fa-user-check me-1"></i> Activate User';
        }
    }
    
    updateSidebarInfo(user) {
        // Update status badge
        const statusElements = document.querySelectorAll('.status-badge');
        statusElements.forEach(element => {
            if (user.is_active) {
                element.className = 'status-badge status-active';
                element.textContent = 'Active';
            } else {
                element.className = 'status-badge status-inactive';
                element.textContent = 'Inactive';
            }
        });
        
        // Update role badge
        const roleElements = document.querySelectorAll('.admin-badge');
        const roleContainers = document.querySelectorAll('.info-value');
        roleContainers.forEach(container => {
            if (container.textContent.trim().includes('ADMIN') || container.textContent.trim() === 'User') {
                if (user.is_admin) {
                    container.innerHTML = '<span class="admin-badge">ADMIN</span>';
                } else {
                    container.textContent = 'User';
                }
            }
        });
        
        // Update admin checkbox to reflect current state
        const adminCheckbox = document.getElementById('is_admin');
        if (adminCheckbox) {
            adminCheckbox.checked = user.is_admin;
        }
    }
    
    showLoading(buttonId, loadingText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            button.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i> ${loadingText}`;
        }
    }
    
    hideLoading(buttonId, originalText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }
    
    showSuccess(message) {
        const successDiv = document.getElementById('edit-user-success-message');
        const errorDiv = document.getElementById('edit-user-error-message');
        
        if (errorDiv) errorDiv.style.display = 'none';
        
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.style.display = 'block';
            
            // Scroll to top to show the message
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Hide after 5 seconds
            setTimeout(() => {
                successDiv.style.display = 'none';
            }, 5000);
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('edit-user-error-message');
        const successDiv = document.getElementById('edit-user-success-message');
        
        if (successDiv) successDiv.style.display = 'none';
        
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            // Scroll to top to show the message
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Hide after 8 seconds
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 8000);
        }
    }
}

// Initialize the edit user manager when the page loads
let editUserManager;

document.addEventListener('DOMContentLoaded', function() {
    editUserManager = new EditUserManager();
});
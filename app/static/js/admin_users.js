// Admin Users Management JavaScript

class AdminUsersManager {
    constructor() {
        this.users = [];
        this.currentUser = null;
        this.isImpersonating = false;
        
        this.init();
    }
    
    async init() {
        await this.loadCurrentUser();
        await this.loadUsers();
        this.setupEventListeners();
        this.checkImpersonationStatus();
    }
    
    async loadCurrentUser() {
        try {
            const response = await fetch('/api/v1/users/me');
            if (response.ok) {
                this.currentUser = await response.json();
            }
        } catch (error) {
            console.error('Error loading current user:', error);
        }
    }
    
    async loadUsers() {
        const loadingState = document.getElementById('loadingState');
        const usersTable = document.getElementById('usersTable');
        const errorMessage = document.getElementById('errorMessage');
        
        try {
            loadingState.style.display = 'block';
            usersTable.style.display = 'none';
            errorMessage.style.display = 'none';
            
            const response = await fetch('/api/v1/users/?limit=1000');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.users = await response.json();
            this.renderUsersTable();
            
            loadingState.style.display = 'none';
            usersTable.style.display = 'block';
            
        } catch (error) {
            console.error('Error loading users:', error);
            loadingState.style.display = 'none';
            this.showError('Failed to load users. Please make sure you have admin privileges.');
        }
    }
    
    renderUsersTable() {
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';
        
        this.users.forEach(user => {
            const row = this.createUserRow(user);
            tbody.appendChild(row);
        });
    }
    
    createUserRow(user) {
        const row = document.createElement('tr');
        
        // Format date
        const createdDate = new Date(user.created_at).toLocaleDateString();
        
        // Status badge
        const statusClass = user.is_active ? 'status-active' : 'status-inactive';
        const statusText = user.is_active ? 'Active' : 'Inactive';
        
        // Role badge
        const roleBadge = user.is_admin ? '<span class="admin-badge">ADMIN</span>' : 'User';
        
        // Action buttons
        const isCurrentUser = user.username === this.currentUser?.username;
        
        // Toggle button
        const toggleClass = user.is_active ? 'toggle-btn' : 'toggle-btn inactive';
        const toggleText = user.is_active ? 'Deactivate' : 'Activate';
        const toggleBtn = isCurrentUser ? 
            `<button class="toggle-btn" disabled>Cannot Toggle Self</button>` :
            `<button class="${toggleClass}" onclick="adminUsersManager.toggleUserActive(${user.id}, ${user.is_active})">
                ${toggleText}
            </button>`;
        
        // Edit button
        const editBtn = `<a href="/ui/admin/users/${user.id}/edit" class="edit-btn" style="text-decoration: none; display: inline-block;">
            Edit
        </a>`;
        
        // Impersonate button (disabled for inactive users, current user, and if user is admin)
        const canImpersonate = user.is_active && 
                              user.username !== this.currentUser?.username && 
                              !user.is_admin;
        
        const impersonateBtn = canImpersonate ? 
            `<button class="impersonate-btn" onclick="adminUsersManager.impersonateUser('${user.username}')">
                Impersonate
            </button>` :
            `<button class="impersonate-btn" disabled>
                ${user.username === this.currentUser?.username ? 'Current User' : 
                  user.is_admin ? 'Admin User' : 'Cannot Impersonate'}
            </button>`;
        
        row.innerHTML = `
            <td>${user.id}</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.email || '<em>No email</em>'}</td>
            <td>${user.display_name || '<em>No display name</em>'}</td>
            <td><span class="user-status ${statusClass}">${statusText}</span></td>
            <td>${roleBadge}</td>
            <td>${createdDate}</td>
            <td>
                <div class="action-buttons">
                    ${toggleBtn}
                    ${editBtn}
                    ${impersonateBtn}
                </div>
            </td>
        `;
        
        return row;
    }
    
    async toggleUserActive(userId, currentStatus) {
        const action = currentStatus ? 'deactivate' : 'activate';
        
        if (!confirm(`Are you sure you want to ${action} this user?`)) {
            return;
        }
        
        try {
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
            
            // Update the user in our local array
            const userIndex = this.users.findIndex(u => u.id === userId);
            if (userIndex !== -1) {
                this.users[userIndex] = updatedUser;
            }
            
            // Re-render the table
            this.renderUsersTable();
            
            this.showSuccess(`User successfully ${action}d.`);
            
        } catch (error) {
            console.error(`Error ${action}ing user:`, error);
            this.showError(`Failed to ${action} user: ${error.message}`);
        }
    }
    
    
    async impersonateUser(username) {
        if (!confirm(`Are you sure you want to impersonate user "${username}"?`)) {
            return;
        }
        
        try {
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
            
            // Show impersonation notice
            this.showImpersonationNotice(username);
            
            // Show success message
            this.showSuccess(`Successfully impersonating user "${username}". You can now navigate to other pages as this user.`);
            
            // Reload the page to reflect the new session
            setTimeout(() => {
                window.location.reload();
            }, 2000);
            
        } catch (error) {
            console.error('Error impersonating user:', error);
            this.showError(`Failed to impersonate user: ${error.message}`);
        }
    }
    
    async stopImpersonation() {
        try {
            const response = await fetch('/api/v1/auth/stop-impersonation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to stop impersonation');
            }
            
            // Hide impersonation notice
            this.hideImpersonationNotice();
            
            // Show success message
            this.showSuccess('Impersonation stopped. Returning to admin session.');
            
            // Reload the page to reflect the original session
            setTimeout(() => {
                window.location.reload();
            }, 1500);
            
        } catch (error) {
            console.error('Error stopping impersonation:', error);
            this.showError(`Failed to stop impersonation: ${error.message}`);
        }
    }
    
    checkImpersonationStatus() {
        // Check if we're currently impersonating by examining the token
        // This would require decoding the JWT or having an endpoint to check status
        // For now, we'll check based on URL parameters or session storage
        const urlParams = new URLSearchParams(window.location.search);
        const impersonating = urlParams.get('impersonating');
        
        if (impersonating) {
            this.showImpersonationNotice(impersonating);
        }
    }
    
    showImpersonationNotice(username) {
        const notice = document.getElementById('impersonationNotice');
        const userSpan = document.getElementById('impersonatedUser');
        
        userSpan.textContent = username;
        notice.style.display = 'block';
        this.isImpersonating = true;
    }
    
    hideImpersonationNotice() {
        const notice = document.getElementById('impersonationNotice');
        notice.style.display = 'none';
        this.isImpersonating = false;
    }
    
    setupEventListeners() {
        // Stop impersonation button
        const stopBtn = document.getElementById('stopImpersonationBtn');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopImpersonation());
        }
        
    }
    
    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
    
    showSuccess(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success';
        successDiv.style.cssText = `
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
        `;
        successDiv.textContent = message;
        
        const container = document.querySelector('.users-container');
        container.insertBefore(successDiv, container.firstChild);
        
        // Remove after 3 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }
}

// Initialize the admin users manager when the page loads
let adminUsersManager;

document.addEventListener('DOMContentLoaded', function() {
    adminUsersManager = new AdminUsersManager();
});
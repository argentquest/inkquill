class BillingDashboard {
    constructor() {
        this.init();
    }
    
    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
    }
    
    async loadDashboardData() {
        try {
            console.log('Loading billing dashboard data...');
            const response = await fetch('/api/v1/billing/dashboard');
            console.log('Dashboard API response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Dashboard data received:', data);
            
            this.updateAccountSummary(data.account);
            this.renderCreditPackages(data.available_packages);
            this.renderTransactions(data.recent_transactions);
            
        } catch (error) {
            console.error('Error loading billing dashboard:', error);
            this.showNotification('Error loading billing data: ' + error.message, 'error');
        }
    }
    
    updateAccountSummary(account) {
        console.log('Updating account summary with:', account);
        
        const balanceElement = document.querySelector('#current-balance .balance-amount');
        const creditsElement = document.querySelector('#total-credits .credits-amount');
        const spentElement = document.querySelector('#total-spent .spent-amount');
        
        console.log('Balance element found:', !!balanceElement);
        console.log('Credits element found:', !!creditsElement);
        console.log('Spent element found:', !!spentElement);
        
        if (balanceElement) {
            balanceElement.textContent = parseFloat(account.current_balance).toFixed(0);
        }
        if (creditsElement) {
            creditsElement.textContent = parseFloat(account.total_credits_added).toFixed(0);
        }
        if (spentElement) {
            spentElement.textContent = parseFloat(account.total_spent).toFixed(0);
        }
    }
    
    renderCreditPackages(packages) {
        console.log('Rendering credit packages:', packages);
        const container = document.getElementById('credit-packages');
        console.log('Credit packages container found:', !!container);
        
        if (!container) {
            console.error('Credit packages container not found!');
            return;
        }
        
        container.innerHTML = '';
        
        if (!packages || packages.length === 0) {
            console.log('No credit packages to render');
            container.innerHTML = '<div class="col-12"><p class="text-muted">No credit packages available</p></div>';
            return;
        }
        
        packages.forEach(pkg => {
            const packageCard = document.createElement('div');
            packageCard.className = 'col-md-3 mb-3';
            
            const bonusText = pkg.bonus_percentage > 0 ? 
                `<span class="badge bg-success">+${pkg.bonus_percentage}% Bonus</span>` : '';
            
            packageCard.innerHTML = `
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">${pkg.name}</h5>
                        <p class="card-text small">${pkg.description || ''}</p>
                        <h4 class="text-primary">
                            <i class="fas fa-coins me-1"></i>
                            ${Math.floor(pkg.credit_amount)} Coins
                        </h4>
                        <p class="text-muted">for $${pkg.price_usd}</p>
                        ${bonusText}
                        <button class="btn btn-primary w-100 mt-2" 
                                onclick="billingDashboard.selectCreditPackage(${pkg.id}, '${pkg.name}', ${pkg.credit_amount}, ${pkg.price_usd}, ${pkg.bonus_percentage})">
                            <i class="fas fa-shopping-cart me-1"></i>
                            Purchase
                        </button>
                    </div>
                </div>
            `;
            
            container.appendChild(packageCard);
        });
    }
    
    renderTransactions(transactions) {
        const tbody = document.querySelector('#transactions-table tbody');
        tbody.innerHTML = '';
        
        if (transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No transactions yet</td></tr>';
            return;
        }
        
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            const amountClass = tx.amount >= 0 ? 'text-success' : 'text-danger';
            const amountSign = tx.amount >= 0 ? '+' : '';
            
            // Format transaction type for display
            const typeDisplay = tx.transaction_type.replace(/_/g, ' ')
                .split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            
            row.innerHTML = `
                <td>${new Date(tx.created_at).toLocaleDateString()}</td>
                <td><span class="badge bg-secondary">${typeDisplay}</span></td>
                <td class="${amountClass}">${amountSign}${Math.floor(Math.abs(tx.amount))} Coins</td>
                <td>${Math.floor(tx.balance_after)} Coins</td>
                <td>${tx.description || ''}</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    selectCreditPackage(id, name, credits, price, bonus) {
        document.getElementById('selected-package-id').value = id;
        
        const bonusText = bonus > 0 ? ` (includes ${bonus}% bonus)` : '';
        document.getElementById('selected-package-info').innerHTML = `
            <strong>${name}</strong><br>
            <i class="fas fa-coins me-1"></i>${credits} Coins for $${price}${bonusText}
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('addCreditsModal'));
        modal.show();
    }
    
    setupEventListeners() {
        document.getElementById('confirm-add-credits').addEventListener('click', () => {
            this.addCredits();
        });
    }
    
    async addCredits() {
        const packageId = document.getElementById('selected-package-id').value;
        const paymentReference = document.getElementById('payment-reference').value;
        
        if (!paymentReference.trim()) {
            this.showNotification('Please enter a payment reference', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/v1/billing/add-credits', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    credit_package_id: parseInt(packageId),
                    payment_reference: paymentReference
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showNotification(`Successfully added ${result.credits_added} Coins!`, 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCreditsModal'));
                modal.hide();
                document.getElementById('add-credits-form').reset();
                
                // Reload dashboard data
                await this.loadDashboardData();
            } else {
                this.showNotification(result.error || 'Failed to add credits', 'error');
            }
            
        } catch (error) {
            console.error('Error adding credits:', error);
            this.showNotification('Error processing credit addition', 'error');
        }
    }
    
    showNotification(message, type) {
        const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize when page loads
console.log('billing_dashboard.js loaded!');
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired in billing_dashboard.js');
    window.billingDashboard = new BillingDashboard();
});
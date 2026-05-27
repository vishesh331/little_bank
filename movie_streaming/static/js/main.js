/**
 * CinemaStream - Main JavaScript
 * Frontend logic for movie streaming application
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Setup event listeners
    setupGlobalListeners();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        initTooltips();
    }

    // Smooth page transitions
    setupPageTransitions();
});

/**
 * Setup global event listeners
 */
function setupGlobalListeners() {
    // Close modals on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
        }
    });

    // Prevent multiple form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtns = this.querySelectorAll('button[type="submit"]');
            submitBtns.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.6';
            });
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup smooth page transitions
 */
function setupPageTransitions() {
    const links = document.querySelectorAll('a[href^="/"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't intercept if it's opening in a new tab
            if (e.ctrlKey || e.metaKey || e.shiftKey) {
                return;
            }

            // Don't intercept logout or modal triggers
            if (this.classList.contains('logout-btn') || 
                this.getAttribute('data-bs-toggle') === 'modal' ||
                this.target === '_blank') {
                return;
            }

            e.preventDefault();
            
            // Add fade out effect
            const main = document.querySelector('main');
            if (main) {
                main.style.opacity = '0';
                main.style.transition = 'opacity 0.3s ease';
            }

            // Navigate after animation
            setTimeout(() => {
                window.location.href = this.href;
            }, 150);
        });
    });
}

/**
 * Fetch user balance
 */
async function fetchBalance() {
    try {
        const response = await fetch('/api/balance');
        const data = await response.json();
        return data.balance;
    } catch (error) {
        console.error('Error fetching balance:', error);
        return null;
    }
}

/**
 * Update balance display in navbar
 */
function updateBalanceDisplay(balance) {
    const balanceEl = document.getElementById('nav-balance');
    if (balanceEl) {
        balanceEl.textContent = balance.toFixed(2);
    }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    const container = document.getElementById('toastContainer') || createToastContainer();
    const toastEl = document.createElement('div');
    toastEl.innerHTML = toastHTML;
    container.appendChild(toastEl);

    const toast = new bootstrap.Toast(toastEl.querySelector('.toast'));
    toast.show();

    // Remove from DOM after hiding
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        width: 300px;
        max-width: 90vw;
    `;
    document.body.appendChild(container);
    return container;
}

/**
 * Debounce function for search
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Throttle function
 */
function throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastCall >= delay) {
            lastCall = now;
            func.apply(this, args);
        }
    };
}

/**
 * Show loading spinner
 */
function showSpinner(element) {
    if (!element) return;
    element.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
}

/**
 * Hide loading spinner
 */
function hideSpinner(element) {
    if (!element) return;
    element.innerHTML = '';
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    const userAccount = document.querySelector('meta[data-user-account]');
    return !!userAccount;
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Validate email
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Log action for analytics (optional)
 */
function logAction(action, data = {}) {
    console.log(`[Action] ${action}`, data);
    // Could send to analytics service here
}

/**
 * Handle API errors consistently
 */
function handleApiError(error) {
    console.error('API Error:', error);
    
    if (error.response) {
        // Server responded with error status
        return {
            status: error.response.status,
            message: error.response.data?.error || 'An error occurred'
        };
    } else if (error.request) {
        // Request made but no response
        return {
            status: 0,
            message: 'No response from server'
        };
    } else {
        // Error in setup
        return {
            status: -1,
            message: error.message || 'An error occurred'
        };
    }
}

/**
 * Setup offline detection
 */
function setupOfflineDetection() {
    window.addEventListener('offline', () => {
        showToast('You are offline. Some features may not work.', 'warning');
    });

    window.addEventListener('online', () => {
        showToast('You are back online!', 'success');
    });
}

// Initialize offline detection
setupOfflineDetection();

// Export functions for use in templates
window.formatCurrency = formatCurrency;
window.showToast = showToast;
window.fetchBalance = fetchBalance;
window.updateBalanceDisplay = updateBalanceDisplay;
window.logAction = logAction;

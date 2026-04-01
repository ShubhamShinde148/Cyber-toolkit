/* ===================================
   Dark Web Leak Monitor - Main JavaScript
   =================================== */

// ===================================
// Navigation Toggle (Mobile)
// ===================================
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    const navbar = document.querySelector('.navbar');
    
    // Navbar scroll effect - add/remove 'scrolled' class
    function handleNavbarScroll() {
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    }
    
    // Initial check and add scroll listener
    handleNavbarScroll();
    window.addEventListener('scroll', handleNavbarScroll, { passive: true });
    
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Close mobile nav when clicking outside
    document.addEventListener('click', function(e) {
        if (navLinks && navLinks.classList.contains('active')) {
            if (!navLinks.contains(e.target) && !navToggle.contains(e.target)) {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            }
        }
    });
    
    // Handle dropdown menus on mobile
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const dropdown = this.closest('.nav-dropdown');
                if (dropdown) {
                    dropdown.classList.toggle('active');
                }
            }
        });
    });
});

const originalFetch = window.fetch.bind(window);

window.fetch = async function(input, init) {
    const response = await originalFetch(input, init);
    const requestUrl = typeof input === 'string' ? input : input.url;
    const isProtectedApi = typeof requestUrl === 'string' && requestUrl.startsWith('/api/');

    if (response.status === 401 && isProtectedApi) {
        try {
            const payload = await response.clone().json();
            if (payload.login_url) {
                window.location.href = payload.login_url;
            }
        } catch (error) {
            window.location.href = '/login';
        }
    }

    return response;
};

// ===================================
// Password Toggle Visibility
// ===================================
function togglePassword(inputId, button = null) {
    const input = document.getElementById(inputId);
    const toggleButton = button || input?.closest('.password-input-wrapper, .input-group, .input-wrapper')?.querySelector('.toggle-password');
    const icon = toggleButton ? toggleButton.querySelector('i') : null;

    if (!input) {
        return;
    }
    
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}

// ===================================
// Toast Notifications
// ===================================
function showToast(message, type = 'info') {
    const container = document.querySelector('.toast-container') || createToastContainer();
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ===================================
// Loading Overlay
// ===================================
function showLoading(message = 'Processing...') {
    let overlay = document.querySelector('.loading-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <p>${message}</p>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('p').textContent = message;
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// ===================================
// Copy to Clipboard
// ===================================
async function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    try {
        await navigator.clipboard.writeText(text);
        showToast(successMessage, 'success');
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            showToast(successMessage, 'success');
            return true;
        } catch (e) {
            showToast('Failed to copy', 'error');
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

// ===================================
// Format Numbers
// ===================================
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// ===================================
// Debounce Function
// ===================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===================================
// Password Strength Calculator
// ===================================
function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];
    
    if (!password) {
        return { score: 0, strength: 'None', color: '#64748b', feedback: ['Enter a password'] };
    }
    
    // Length scoring
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (password.length >= 16) score += 1;
    
    // Character variety
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^a-zA-Z0-9]/.test(password)) score += 1;
    
    // Penalties
    if (/^[a-zA-Z]+$/.test(password)) score -= 1;
    if (/^[0-9]+$/.test(password)) score -= 1;
    if (/(.)\1{2,}/.test(password)) score -= 1;
    
    // Normalize score
    score = Math.max(0, Math.min(5, score));
    
    const strengths = [
        { strength: 'Very Weak', color: '#ef4444' },
        { strength: 'Weak', color: '#f97316' },
        { strength: 'Fair', color: '#f59e0b' },
        { strength: 'Good', color: '#84cc16' },
        { strength: 'Strong', color: '#22c55e' },
        { strength: 'Very Strong', color: '#10b981' }
    ];
    
    // Generate feedback
    if (password.length < 8) feedback.push('Use at least 8 characters');
    if (!/[A-Z]/.test(password)) feedback.push('Add uppercase letters');
    if (!/[a-z]/.test(password)) feedback.push('Add lowercase letters');
    if (!/[0-9]/.test(password)) feedback.push('Add numbers');
    if (!/[^a-zA-Z0-9]/.test(password)) feedback.push('Add special characters');
    
    return {
        score: score,
        strength: strengths[score].strength,
        color: strengths[score].color,
        percentage: (score / 5) * 100,
        feedback: feedback
    };
}

// ===================================
// Validate Email
// ===================================
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// ===================================
// Format Date
// ===================================
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// ===================================
// Smooth Scroll to Element
// ===================================
function scrollToElement(elementId, offset = 100) {
    const element = document.getElementById(elementId);
    if (element) {
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
    }
}

// ===================================
// API Helper Functions
// ===================================
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ===================================
// Local Storage Helpers
// ===================================
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Storage error:', e);
        return false;
    }
}

function getFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Storage error:', e);
        return defaultValue;
    }
}

// ===================================
// Theme Toggle (Future Feature)
// ===================================
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    saveToStorage('theme', newTheme);
}

// Initialize theme from storage
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = getFromStorage('theme', 'dark');
    document.documentElement.setAttribute('data-theme', savedTheme);
});

// ===================================
// Export Functions for Global Use
// ===================================
window.togglePassword = togglePassword;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.copyToClipboard = copyToClipboard;
window.formatNumber = formatNumber;
window.calculatePasswordStrength = calculatePasswordStrength;
window.isValidEmail = isValidEmail;
window.scrollToElement = scrollToElement;
window.apiRequest = apiRequest;

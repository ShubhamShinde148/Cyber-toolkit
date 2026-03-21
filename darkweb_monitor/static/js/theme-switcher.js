/**
 * Dark Web Leak Monitor - Advanced Theme Switcher
 * Handles dynamically loading, saving, and applying multi-theme UI styles.
 */

class ThemeManager {
    constructor() {
        // Theme definitions matching themes.css data-themes
        this.themes = {
            'default': { name: 'Cyber Green', icon: 'fa-user-secret' },
            'purple': { name: 'Purple Hacker', icon: 'fa-mask' },
            'blue': { name: 'Blue Security', icon: 'fa-shield-virus' },
            'red': { name: 'Red Threat', icon: 'fa-biohazard' },
            'light': { name: 'Light Mode', icon: 'fa-sun' },
            'soc': { name: 'SOC Analyst', icon: 'fa-network-wired' }
        };
        
        // Ensure theme is applied before page fully loads to avoid flickering
        this.init();
    }

    init() {
        const savedTheme = localStorage.getItem('app-theme') || 'default';
        this.applyTheme(savedTheme, false);
        
        // Wait for DOM to bind events
        document.addEventListener('DOMContentLoaded', () => {
            this.bindDropdownEvents();
            this.updateActiveUIState(savedTheme);
        });
    }

    applyTheme(themeId, animate = true) {
        if (!this.themes[themeId]) themeId = 'default';
        
        if (animate) {
            document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        } else {
            document.documentElement.style.transition = 'none';
        }

        if (themeId === 'default') {
            document.documentElement.removeAttribute('data-theme');
        } else {
            document.documentElement.setAttribute('data-theme', themeId);
        }

        localStorage.setItem('app-theme', themeId);
        this.updateActiveUIState(themeId);
    }

    updateActiveUIState(themeId) {
        // Update the active state in the dropdown menu
        const dropdownItems = document.querySelectorAll('.theme-option');
        if (dropdownItems.length === 0) return;

        dropdownItems.forEach(item => {
            if (item.getAttribute('data-theme-value') === themeId) {
                item.classList.add('active-theme');
                item.querySelector('.theme-check').style.opacity = '1';
            } else {
                item.classList.remove('active-theme');
                item.querySelector('.theme-check').style.opacity = '0';
            }
        });

        // Update the main navbar icon to match current theme
        const navIcon = document.getElementById('currentThemeIcon');
        const navText = document.getElementById('currentThemeText');
        if (navIcon && this.themes[themeId]) {
            navIcon.className = `fas ${this.themes[themeId].icon}`;
        }
        if (navText && this.themes[themeId]) {
            navText.textContent = this.themes[themeId].name;
        }
    }

    bindDropdownEvents() {
        const themeOptions = document.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const selectedTheme = option.getAttribute('data-theme-value');
                this.applyTheme(selectedTheme);
            });
        });
    }
}

// Global initialization
window.themeManager = new ThemeManager();

// Global wrapper for inline HTML onclick handlers just in case
window.changeAppTheme = function(themeId) {
    if (window.themeManager) {
        window.themeManager.applyTheme(themeId);
    }
};

/**
 * Dark Web Leak Monitor - Animation Manager
 * Bridges the UI controls with the CyberParticleSystem and handles persistence.
 */

class AnimationManager {
    constructor() {
        this.modes = {
            'particles': { name: 'Cyber Particles', icon: 'fa-project-diagram' },
            'matrix': { name: 'Matrix Rain', icon: 'fa-barcode' },
            'hex': { name: 'Hex Scan', icon: 'fa-draw-polygon' },
            'grid': { name: 'Dark Grid', icon: 'fa-border-all' },
            'secure': { name: 'Secure Node', icon: 'fa-network-wired' }
        };
        
        this.init();
    }

    init() {
        // Wait for both DOM and the CyberParticleSystem to be available
        document.addEventListener('DOMContentLoaded', () => {
            const savedMode = localStorage.getItem('app-animation-mode') || 'particles';
            
            // Interval check as cyber-particles.js might load slightly before or after
            const checkInterval = setInterval(() => {
                if (window.cyberParticles) {
                    clearInterval(checkInterval);
                    this.applyMode(savedMode, false);
                    this.bindEvents();
                    this.updateUI(savedMode);
                }
            }, 100);
            
            // Timeout safety
            setTimeout(() => clearInterval(checkInterval), 5000);
        });
    }

    applyMode(mode, save = true) {
        if (!this.modes[mode]) mode = 'particles';
        
        if (window.cyberParticles) {
            window.cyberParticles.setMode(mode);
        }
        
        if (save) {
            localStorage.setItem('app-animation-mode', mode);
        }
        
        this.updateUI(mode);
    }

    updateUI(mode) {
        const optionItems = document.querySelectorAll('.animation-option');
        optionItems.forEach(item => {
            const itemMode = item.getAttribute('data-anim-value');
            if (itemMode === mode) {
                item.classList.add('active-anim');
                const check = item.querySelector('.anim-check');
                if (check) check.style.opacity = '1';
            } else {
                item.classList.remove('active-anim');
                const check = item.querySelector('.anim-check');
                if (check) check.style.opacity = '0';
            }
        });

        // Update main button label if it exists
        const currentIcon = document.getElementById('currentAnimIcon');
        const currentText = document.getElementById('currentAnimText');
        if (currentIcon && this.modes[mode]) {
            currentIcon.className = `fas ${this.modes[mode].icon}`;
        }
        if (currentText && this.modes[mode]) {
            currentText.textContent = this.modes[mode].name;
        }
    }

    bindEvents() {
        const optionItems = document.querySelectorAll('.animation-option');
        optionItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const mode = item.getAttribute('data-anim-value');
                this.applyMode(mode);
            });
        });
    }
}

// Global initialization
window.animationManager = new AnimationManager();

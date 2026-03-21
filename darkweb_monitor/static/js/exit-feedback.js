/* ===================================
   Exit Feedback - Intent Detection & Modal Control
   Dark Web Leak Monitor
   =================================== */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        exitIntentThreshold: 50,      // Pixels from top to trigger exit intent
        scrollThreshold: 30,          // Percentage of page scrolled before enabling
        timeOnPageMin: 5000,          // Minimum time on page before showing (5 seconds)
        sessionKey: 'dwlm_feedback_shown',
        feedbackEndpoint: '/api/feedback'
    };
    
    // State
    let state = {
        modalShown: false,
        isSubmitting: false,
        selectedRating: 0,
        pageLoadTime: Date.now(),
        hasScrolled: false,
        exitIntentEnabled: false
    };
    
    // DOM Elements (cached after init)
    let elements = {};
    
    // Rating text descriptions
    const ratingTexts = {
        1: 'Poor - Needs improvement',
        2: 'Fair - Could be better',
        3: 'Good - Met expectations',
        4: 'Great - Above average',
        5: 'Excellent - Outstanding!'
    };
    
    // ===================================
    // Initialization
    // ===================================
    
    function init() {
        // Always cache DOM elements for manual API use
        cacheElements();
        
        if (!elements.overlay) {
            console.log('[ExitFeedback] Modal elements not found');
            return;
        }
        
        // Always set up modal interactions (for manual triggering via API)
        setupModalInteractions();
        
        // Check if feedback was already shown this session - skip auto-detection
        if (sessionStorage.getItem(CONFIG.sessionKey)) {
            console.log('[ExitFeedback] Already shown this session (manual trigger still available)');
            return;
        }
        
        // Set up exit intent detection (only if not shown this session)
        setupExitIntentDetection();
        setupScrollTracking();
        
        // Enable exit intent after minimum time
        setTimeout(() => {
            state.exitIntentEnabled = true;
            console.log('[ExitFeedback] Exit intent detection enabled');
        }, CONFIG.timeOnPageMin);
    }
    
    function cacheElements() {
        elements = {
            overlay: document.getElementById('exitFeedbackOverlay'),
            modal: document.getElementById('exitFeedbackModal'),
            form: document.getElementById('exitFeedbackForm'),
            starRating: document.getElementById('starRating'),
            ratingText: document.getElementById('ratingText'),
            feedbackText: document.getElementById('feedbackText'),
            charCount: document.getElementById('charCount'),
            submitBtn: document.getElementById('submitFeedback'),
            skipBtn: document.getElementById('skipFeedback'),
            closeBtn: document.getElementById('closeFeedback'),
            thankyou: document.getElementById('feedbackThankyou'),
            thankyouStars: document.getElementById('thankyouStars')
        };
    }
    
    // ===================================
    // Exit Intent Detection
    // ===================================
    
    function setupExitIntentDetection() {
        // Primary: mouseleave on document - fires when cursor leaves the page
        document.documentElement.addEventListener('mouseleave', handleMouseLeave);
        
        // Fallback: mouseout on document for broader compatibility
        document.addEventListener('mouseout', handleMouseExit);
        
        // Before unload (closing tab, refreshing)
        window.addEventListener('beforeunload', handleBeforeUnload);
    }
    
    function handleMouseLeave(e) {
        // Trigger when mouse leaves through the top of the viewport
        if (e.clientY < 0 && canShowModal()) {
            showFeedbackModal('exit_intent');
        }
    }
    
    function handleMouseExit(e) {
        // Fallback: check if mouse is leaving through the top
        if (e.clientY <= CONFIG.exitIntentThreshold && 
            !e.relatedTarget && 
            !e.toElement &&
            canShowModal()) {
            showFeedbackModal('exit_intent');
        }
    }
    
    function handleBeforeUnload(e) {
        // Note: Modern browsers restrict what you can do in beforeunload
        // We can't reliably show custom modals, but we track the attempt
        if (canShowModal() && !state.modalShown) {
            // Trigger the modal - user might cancel the navigation
            showFeedbackModal('page_exit');
        }
    }
    
    function canShowModal() {
        const timeOnPage = Date.now() - state.pageLoadTime;
        return (
            state.exitIntentEnabled &&
            !state.modalShown &&
            timeOnPage >= CONFIG.timeOnPageMin &&
            !sessionStorage.getItem(CONFIG.sessionKey)
        );
    }
    
    // ===================================
    // Scroll Tracking
    // ===================================
    
    function setupScrollTracking() {
        let ticking = false;
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
                    
                    if (scrollPercent >= CONFIG.scrollThreshold) {
                        state.hasScrolled = true;
                    }
                    
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }
    
    // ===================================
    // Modal Display & Animation
    // ===================================
    
    function showFeedbackModal(trigger = 'manual') {
        if (state.modalShown) return;
        
        // Ensure elements exist
        if (!elements.overlay || !elements.modal) {
            console.error('[ExitFeedback] Cannot show modal - required elements missing');
            return;
        }
        
        state.modalShown = true;
        sessionStorage.setItem(CONFIG.sessionKey, 'true');
        
        // Show overlay with animation
        elements.overlay.classList.remove('hidden');
        
        // Trigger entrance animation
        requestAnimationFrame(() => {
            elements.overlay.classList.add('active');
            elements.modal.classList.add('animate-in');
        });
        
        // Focus management for accessibility
        elements.modal.setAttribute('role', 'dialog');
        elements.modal.setAttribute('aria-modal', 'true');
        
        // Trap focus inside modal
        trapFocus(elements.modal);
        
        console.log(`[ExitFeedback] Modal shown (trigger: ${trigger})`);
    }
    
    function hideFeedbackModal(reason = 'closed') {
        if (!elements.overlay || !elements.modal) {
            console.warn('[ExitFeedback] Cannot hide modal - elements missing');
            return;
        }
        
        elements.overlay.classList.remove('active');
        elements.modal.classList.remove('animate-in');
        elements.modal.classList.add('animate-out');
        
        setTimeout(() => {
            elements.overlay.classList.add('hidden');
            elements.modal.classList.remove('animate-out');
        }, 300);
        
        console.log(`[ExitFeedback] Modal hidden (reason: ${reason})`);
    }
    
    // ===================================
    // Modal Interactions
    // ===================================
    
    function setupModalInteractions() {
        // Validate required elements exist
        if (!elements.starRating || !elements.form || !elements.overlay) {
            console.warn('[ExitFeedback] Some required elements missing, skipping interaction setup');
            return;
        }
        
        // Star rating interaction
        const starLabels = elements.starRating.querySelectorAll('.star-label');
        starLabels.forEach(label => {
            label.addEventListener('click', handleStarClick);
            label.addEventListener('mouseenter', handleStarHover);
        });
        
        elements.starRating.addEventListener('mouseleave', handleStarMouseLeave);
        
        // Character counter
        if (elements.feedbackText) {
            elements.feedbackText.addEventListener('input', updateCharCount);
        }
        
        // Form submission
        elements.form.addEventListener('submit', handleSubmit);
        
        // Skip button
        if (elements.skipBtn) {
            elements.skipBtn.addEventListener('click', () => hideFeedbackModal('skipped'));
        }
        
        // Close button
        if (elements.closeBtn) {
            elements.closeBtn.addEventListener('click', () => hideFeedbackModal('closed'));
        }
        
        // Click outside to close
        elements.overlay.addEventListener('click', (e) => {
            if (e.target === elements.overlay) {
                hideFeedbackModal('outside_click');
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.overlay && !elements.overlay.classList.contains('hidden')) {
                hideFeedbackModal('escape');
            }
        });
        
        console.log('[ExitFeedback] Modal interactions initialized');
    }
    
    function handleStarClick(e) {
        const value = parseInt(e.currentTarget.dataset.value);
        state.selectedRating = value;
        
        // Update radio button
        document.getElementById(`star${value}`).checked = true;
        
        // Update visual state
        updateStarDisplay(value, true);
        
        // Update text
        elements.ratingText.textContent = ratingTexts[value];
        elements.ratingText.classList.add('selected');
    }
    
    function handleStarHover(e) {
        const value = parseInt(e.currentTarget.dataset.value);
        updateStarDisplay(value, false);
    }
    
    function handleStarMouseLeave() {
        updateStarDisplay(state.selectedRating, true);
    }
    
    function updateStarDisplay(value, isSelection) {
        const starLabels = elements.starRating.querySelectorAll('.star-label');
        starLabels.forEach(label => {
            const starValue = parseInt(label.dataset.value);
            if (starValue <= value) {
                label.classList.add('active');
                if (isSelection) {
                    label.classList.add('selected');
                }
            } else {
                label.classList.remove('active');
                if (isSelection) {
                    label.classList.remove('selected');
                }
            }
        });
    }
    
    function updateCharCount() {
        const count = elements.feedbackText.value.length;
        elements.charCount.textContent = count;
        
        if (count >= 450) {
            elements.charCount.parentElement.classList.add('warning');
        } else {
            elements.charCount.parentElement.classList.remove('warning');
        }
    }
    
    // ===================================
    // Form Submission
    // ===================================
    
    async function handleSubmit(e) {
        e.preventDefault();
        
        if (state.isSubmitting) return;
        
        // Validate rating
        if (state.selectedRating === 0) {
            elements.ratingText.textContent = 'Please select a rating';
            elements.ratingText.classList.add('error');
            setTimeout(() => {
                elements.ratingText.classList.remove('error');
                elements.ratingText.textContent = 'Select a rating';
            }, 2000);
            return;
        }
        
        state.isSubmitting = true;
        elements.submitBtn.disabled = true;
        elements.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        const feedbackData = {
            rating: state.selectedRating,
            feedback: elements.feedbackText.value.trim(),
            timestamp: new Date().toISOString(),
            page: window.location.pathname,
            userAgent: navigator.userAgent
        };
        
        try {
            const response = await fetch(CONFIG.feedbackEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(feedbackData)
            });
            
            if (response.ok) {
                showThankYou();
            } else {
                // Still show thank you - don't punish user for server errors
                console.warn('[ExitFeedback] Server error, but showing thank you');
                showThankYou();
            }
        } catch (error) {
            console.error('[ExitFeedback] Submission error:', error);
            // Still show thank you for good UX
            showThankYou();
        }
    }
    
    function showThankYou() {
        // Hide form
        elements.form.classList.add('hidden');
        elements.closeBtn.classList.add('hidden');
        
        // Show thank you state
        elements.thankyou.classList.remove('hidden');
        
        // Display stars
        let starsHTML = '';
        for (let i = 0; i < 5; i++) {
            const filled = i < state.selectedRating;
            starsHTML += `<i class="fas fa-star ${filled ? 'filled' : ''}"></i>`;
        }
        elements.thankyouStars.innerHTML = starsHTML;
        
        // Auto-close after delay
        setTimeout(() => {
            hideFeedbackModal('submitted');
        }, 2500);
    }
    
    // ===================================
    // Accessibility - Focus Trap
    // ===================================
    
    function trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        firstFocusable?.focus();
        
        element.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    lastFocusable.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    firstFocusable.focus();
                    e.preventDefault();
                }
            }
        });
    }
    
    // ===================================
    // Public API (for testing/manual trigger)
    // ===================================
    
    window.ExitFeedback = {
        show: () => {
            // Ensure elements are cached
            if (!elements.overlay) {
                cacheElements();
            }
            if (!elements.overlay) {
                console.error('[ExitFeedback] Cannot show - modal elements not found');
                return;
            }
            // Reset state to allow showing
            state.modalShown = false;
            showFeedbackModal('manual');
        },
        hide: () => hideFeedbackModal('manual'),
        reset: () => {
            sessionStorage.removeItem(CONFIG.sessionKey);
            state.modalShown = false;
            state.selectedRating = 0;
            state.isSubmitting = false;
            // Reset form UI
            if (elements.form) {
                elements.form.classList.remove('hidden');
                elements.form.reset();
            }
            if (elements.thankyou) {
                elements.thankyou.classList.add('hidden');
            }
            if (elements.closeBtn) {
                elements.closeBtn.classList.remove('hidden');
            }
            if (elements.ratingText) {
                elements.ratingText.textContent = 'Select a rating';
                elements.ratingText.classList.remove('selected', 'error');
            }
            if (elements.starRating) {
                elements.starRating.querySelectorAll('.star-label').forEach(label => {
                    label.classList.remove('active', 'selected');
                });
            }
            console.log('[ExitFeedback] State reset');
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();

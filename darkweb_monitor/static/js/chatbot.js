/**
 * Dark Web Leak Monitor - Chatbot Widget
 * AI-powered cybersecurity assistant using OpenAI GPT
 */

class CybersecurityChatbot {
    constructor() {
        this.isOpen = false;
        this.isFullscreen = false;
        this.isTyping = false;
        this.conversationHistory = [];
        this.maxHistoryLength = 10;
        
        // DOM Elements
        this.fab = document.getElementById('chatbotFab');
        this.window = document.getElementById('chatbotWindow');
        this.messages = document.getElementById('chatbotMessages');
        this.input = document.getElementById('chatbotInput');
        this.sendBtn = document.getElementById('chatbotSend');
        this.closeBtn = document.getElementById('chatbotClose');
        this.clearBtn = document.getElementById('chatbotClear');
        this.fullscreenBtn = document.getElementById('chatbotFullscreen');
        this.suggestions = document.getElementById('chatbotSuggestions');
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.fab.addEventListener('click', () => this.toggle());
        this.closeBtn.addEventListener('click', () => this.close());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.clearBtn.addEventListener('click', () => this.clearChat());
        this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        
        // Input handling
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.input.addEventListener('input', () => this.autoResizeInput());
        
        // Suggestion buttons
        this.bindSuggestionButtons();
        
        // Check if chatbot is configured
        this.checkStatus();
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !this.window.contains(e.target) && 
                !this.fab.contains(e.target)) {
                // Optional: close on outside click
                // this.close();
            }
        });
        
        // Keyboard shortcut (Ctrl+Shift+C)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                this.toggle();
            }
        });
    }
    
    async checkStatus() {
        try {
            const response = await fetch('/api/chatbot/status');
            const data = await response.json();
            
            if (!data.configured) {
                console.warn('Chatbot: OpenAI API key not configured');
            }
        } catch (error) {
            console.error('Chatbot status check failed:', error);
        }
    }
    
    bindSuggestionButtons() {
        const buttons = this.suggestions.querySelectorAll('.suggestion-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                if (message) {
                    this.input.value = message;
                    this.sendMessage();
                }
            });
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.isOpen = true;
        this.window.classList.add('active');
        this.fab.classList.add('hidden');
        this.input.focus();
        
        // Hide notification
        const notification = document.getElementById('chatbotNotification');
        if (notification) {
            notification.style.display = 'none';
        }
    }
    
    close() {
        this.isOpen = false;
        this.isFullscreen = false;
        this.window.classList.remove('active', 'fullscreen');
        this.fab.classList.remove('hidden');
        this.fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        this.fullscreenBtn.title = 'Fullscreen';
    }
    
    toggleFullscreen() {
        this.isFullscreen = !this.isFullscreen;
        this.window.classList.toggle('fullscreen', this.isFullscreen);
        
        if (this.isFullscreen) {
            this.fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
            this.fullscreenBtn.title = 'Exit Fullscreen';
        } else {
            this.fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
            this.fullscreenBtn.title = 'Fullscreen';
        }
        
        this.scrollToBottom();
    }
    
    autoResizeInput() {
        this.input.style.height = 'auto';
        this.input.style.height = Math.min(this.input.scrollHeight, 100) + 'px';
    }
    
    async sendMessage() {
        const message = this.input.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Clear input
        this.input.value = '';
        this.autoResizeInput();
        
        // Hide suggestions after first message
        if (this.suggestions) {
            this.suggestions.style.display = 'none';
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Add to history
        this.conversationHistory.push({
            role: 'user',
            content: message
        });
        
        // Trim history if needed
        if (this.conversationHistory.length > this.maxHistoryLength * 2) {
            this.conversationHistory = this.conversationHistory.slice(-this.maxHistoryLength * 2);
        }
        
        // Show typing indicator
        this.showTyping();
        
        try {
            // Send to backend
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory.slice(0, -1) // Exclude current message
                })
            });

            let data = null;
            try {
                data = await response.json();
            } catch (parseError) {
                data = null;
            }
            
            // Hide typing indicator
            this.hideTyping();

            if (!response.ok) {
                this.addMessage(
                    (data && data.error) || 'Server error. Please try again later.',
                    'error'
                );
                return;
            }

            if (!data) {
                this.addMessage(
                    'Invalid server response. Please try again later.',
                    'error'
                );
                return;
            }
            
            // Check if message contains HTML (error from proxy/gateway)
            if (data.message && (data.message.includes('<html') || data.message.includes('<!DOCTYPE'))) {
                this.addMessage(
                    'The AI service is temporarily unavailable. Please try again in a moment.',
                    'error'
                );
                return;
            }
            
            if (data.success) {
                // Add bot response
                this.addMessage(data.message, 'bot');
                
                // Add to history
                this.conversationHistory.push({
                    role: 'assistant',
                    content: data.message
                });
            } else {
                // Show error
                this.addMessage(
                    data.error || 'Sorry, I encountered an error. Please try again.',
                    'error'
                );
            }
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTyping();
            this.addMessage(
                'Unable to connect to the server. Please check your connection and try again.',
                'error'
            );
        }
    }
    
    addMessage(content, type = 'bot') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${type}`;
        
        // Avatar icon
        let avatarIcon = 'fa-shield-alt';
        if (type === 'user') {
            avatarIcon = 'fa-user';
        } else if (type === 'error') {
            avatarIcon = 'fa-exclamation-triangle';
        }
        
        // Format content (basic markdown support)
        const formattedContent = this.formatMessage(content);
        
        messageDiv.innerHTML = `
            <div class="chatbot-message-avatar">
                <i class="fas ${avatarIcon}"></i>
            </div>
            <div class="chatbot-message-content">
                ${formattedContent}
            </div>
        `;
        
        this.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Basic markdown formatting
        let formatted = content;
        
        // Escape HTML
        formatted = formatted
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Code blocks (```code```)
        formatted = formatted.replace(
            /```([\s\S]*?)```/g,
            '<pre><code>$1</code></pre>'
        );
        
        // Inline code (`code`)
        formatted = formatted.replace(
            /`([^`]+)`/g,
            '<code>$1</code>'
        );
        
        // Bold (**text**)
        formatted = formatted.replace(
            /\*\*([^*]+)\*\*/g,
            '<strong>$1</strong>'
        );
        
        // Italic (*text*)
        formatted = formatted.replace(
            /\*([^*]+)\*/g,
            '<em>$1</em>'
        );
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Numbered lists (1. item)
        formatted = formatted.replace(
            /^(\d+)\.\s+(.+)$/gm,
            '<li>$2</li>'
        );
        
        // Unordered lists (- item)
        formatted = formatted.replace(
            /^- (.+)$/gm,
            '<li>$1</li>'
        );
        
        // Wrap consecutive <li> blocks in <ul>
        formatted = formatted.replace(
            /((?:<li>.*?<\/li>(?:<br>)?)+)/gs,
            '<ul>$1</ul>'
        );
        
        // Clean up <br> inside lists
        formatted = formatted.replace(/<ul><br>/g, '<ul>');
        formatted = formatted.replace(/<br><\/ul>/g, '</ul>');
        formatted = formatted.replace(/<\/li><br><li>/g, '</li><li>');
        
        return formatted;
    }
    
    showTyping() {
        this.isTyping = true;
        this.sendBtn.disabled = true;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message bot chatbot-typing';
        typingDiv.id = 'chatbotTypingIndicator';
        typingDiv.innerHTML = `
            <div class="chatbot-message-avatar">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="chatbot-typing-indicator">
                <div class="chatbot-typing-dot"></div>
                <div class="chatbot-typing-dot"></div>
                <div class="chatbot-typing-dot"></div>
            </div>
        `;
        
        this.messages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTyping() {
        this.isTyping = false;
        this.sendBtn.disabled = false;
        
        const typingIndicator = document.getElementById('chatbotTypingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    scrollToBottom() {
        this.messages.scrollTop = this.messages.scrollHeight;
    }
    
    clearChat() {
        // Keep only the welcome message
        const welcomeMessage = this.messages.querySelector('.chatbot-message.bot');
        this.messages.innerHTML = '';
        
        if (welcomeMessage) {
            this.messages.appendChild(welcomeMessage.cloneNode(true));
        }
        
        // Reset suggestions
        if (this.suggestions) {
            this.messages.appendChild(this.suggestions.cloneNode(true));
            this.suggestions = this.messages.querySelector('.chatbot-suggestions');
            this.suggestions.style.display = 'flex';
            this.bindSuggestionButtons();
        }
        
        // Clear history
        this.conversationHistory = [];
        
        // Show toast notification
        this.showToast('Chat cleared', 'success');
    }
    
    showToast(message, type = 'info') {
        // Use existing toast system if available
        const toastContainer = document.getElementById('toastContainer');
        if (toastContainer && typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log(`Chatbot: ${message}`);
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new CybersecurityChatbot();
});

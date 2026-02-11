/**
 * TrustLink AI Chatbot Widget
 * Floating chat interface with AI-powered assistance
 */

class TrustLinkChatbot {
    constructor() {
        this.isOpen = false;
        this.isEnabled = false;
        this.conversationHistory = [];
        this.maxHistoryLength = 10;
        this.isTyping = false;
        
        this.init();
    }
    
    async init() {
        // Check if chatbot is enabled
        const status = await this.checkStatus();
        if (!status.enabled) {
            console.log('Chatbot is disabled');
            return;
        }
        
        this.isEnabled = true;
        this.createWidget();
        this.attachEventListeners();
        this.loadSuggestions();
        
        // Add welcoming bounce animation to draw attention (but don't auto-open)
        setTimeout(() => {
            const toggleBtn = document.getElementById('chatbot-toggle');
            if (toggleBtn) {
                toggleBtn.style.animation = 'bounce 0.5s ease';
            }
        }, 2000);
    }
    
    async checkStatus() {
        try {
            const response = await fetch('/api/chat/status');
            return await response.json();
        } catch (error) {
            console.error('Failed to check chatbot status:', error);
            return { enabled: false };
        }
    }
    
    createWidget() {
        // Create chatbot container
        const chatbotHTML = `
            <div id="trustlink-chatbot" class="chatbot-widget">
                <!-- Chat Button -->
                <button id="chatbot-toggle" class="chatbot-toggle" aria-label="Toggle chatbot">
                    <svg class="chatbot-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <svg class="close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
                
                <!-- Chat Window -->
                <div id="chatbot-window" class="chatbot-window">
                    <!-- Header -->
                    <div class="chatbot-header">
                        <div class="chatbot-header-content">
                            <div class="chatbot-avatar">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                                </svg>
                            </div>
                            <div class="chatbot-header-text">
                                <h3>TrustLink AI Assistant</h3>
                                <span class="chatbot-status">Online</span>
                            </div>
                        </div>
                        <button id="chatbot-minimize" class="chatbot-minimize" aria-label="Minimize chat">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Messages Container -->
                    <div id="chatbot-messages" class="chatbot-messages">
                        <div class="chatbot-welcome">
                            <div class="chatbot-avatar-large">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                                </svg>
                            </div>
                            <h4>Hi! I'm TrustLink AI Assistant 👋</h4>
                            <p>I can help you understand phishing threats, explain scan results, and answer security questions.</p>
                        </div>
                        
                        <!-- Suggested Questions -->
                        <div id="chatbot-suggestions" class="chatbot-suggestions"></div>
                    </div>
                    
                    <!-- Input Area -->
                    <div class="chatbot-input-container">
                        <textarea 
                            id="chatbot-input" 
                            class="chatbot-input" 
                            placeholder="Ask me anything about phishing..." 
                            rows="1"
                            maxlength="1000"
                        ></textarea>
                        <button id="chatbot-send" class="chatbot-send" aria-label="Send message">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }
    
    attachEventListeners() {
        const toggleBtn = document.getElementById('chatbot-toggle');
        const minimizeBtn = document.getElementById('chatbot-minimize');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        
        toggleBtn.addEventListener('click', () => this.toggleChat());
        minimizeBtn.addEventListener('click', () => this.toggleChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Send on Enter (but allow Shift+Enter for new line)
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        });
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        const widget = document.getElementById('trustlink-chatbot');
        const toggleBtn = document.getElementById('chatbot-toggle');
        
        if (this.isOpen) {
            widget.classList.add('chatbot-open');
            toggleBtn.classList.add('chatbot-open');
            document.getElementById('chatbot-input').focus();
        } else {
            widget.classList.remove('chatbot-open');
            toggleBtn.classList.remove('chatbot-open');
        }
    }
    
    async loadSuggestions() {
        try {
            const response = await fetch('/api/chat/suggestions');
            const data = await response.json();
            
            if (!data.error && data.suggestions) {
                this.displaySuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        }
    }
    
    displaySuggestions(suggestions) {
        const container = document.getElementById('chatbot-suggestions');
        container.innerHTML = '<div class="suggestions-title">Suggested questions:</div>';
        
        suggestions.slice(0, 4).forEach(suggestion => {
            const button = document.createElement('button');
            button.className = 'suggestion-btn';
            button.textContent = suggestion;
            button.addEventListener('click', () => {
                document.getElementById('chatbot-input').value = suggestion;
                this.sendMessage();
            });
            container.appendChild(button);
        });
    }
    
    async sendMessage(retryCount = 0) {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Clear input and reset height
        input.value = '';
        input.style.height = 'auto';
        
        // Hide suggestions after first message
        const suggestions = document.getElementById('chatbot-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
        
        // Add user message to chat (only on first attempt)
        if (retryCount === 0) {
            this.addMessage(message, 'user');
            
            // Add to conversation history
            this.conversationHistory.push({
                role: 'user',
                content: message
            });
        }
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to API with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory.slice(-this.maxHistoryLength)
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.error) {
                // If AI service is unavailable, provide helpful fallback
                if (data.message.includes('unavailable') || data.message.includes('loading')) {
                    this.addMessage(data.message, 'assistant');
                } else {
                    this.addMessage(data.message || 'Sorry, I encountered an error. Please try again.', 'assistant', true);
                }
            } else {
                // Check if this is a fallback response
                if (data.fallback) {
                    this.addMessage('⏳ The AI is still loading. Here\'s some helpful information:\n\n' + data.message, 'assistant');
                } else {
                    this.addMessage(data.message, 'assistant');
                }
                
                // Add assistant response to history
                this.conversationHistory.push({
                    role: 'assistant',
                    content: data.message
                });
                
                // Keep history manageable
                if (this.conversationHistory.length > this.maxHistoryLength * 2) {
                    this.conversationHistory = this.conversationHistory.slice(-this.maxHistoryLength * 2);
                }
            }
        } catch (error) {
            this.hideTypingIndicator();
            
            // Retry logic for connection issues
            if (retryCount < 2 && (error.name === 'AbortError' || error.message.includes('fetch'))) {
                console.log(`Retry attempt ${retryCount + 1}/2`);
                this.addMessage(`⏳ Connection issue detected. Retrying (${retryCount + 1}/2)...`, 'assistant');
                
                // Wait 2 seconds before retry
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Remove retry message
                const messages = document.getElementById('chatbot-messages');
                const lastMessage = messages.lastElementChild;
                if (lastMessage && lastMessage.textContent.includes('Retrying')) {
                    lastMessage.remove();
                }
                
                // Retry the request
                return this.sendMessage(retryCount + 1);
            }
            
            this.addMessage('Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'assistant', true);
            console.error('Chat error:', error);
        }
    }
    
    addMessage(text, role, isError = false) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${role}-message ${isError ? 'error-message' : ''}`;
        
        if (role === 'assistant') {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <div class="message-content">${this.formatMessage(text)}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">${this.escapeHtml(text)}</div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chatbot-message assistant-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    formatMessage(text) {
        // Convert markdown-style formatting to HTML
        let formatted = this.escapeHtml(text);
        
        // Bold text **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Bullet points
        formatted = formatted.replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new TrustLinkChatbot();
    });
} else {
    new TrustLinkChatbot();
}

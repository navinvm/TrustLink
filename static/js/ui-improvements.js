/**
 * TrustLink UI Improvements
 * Toast notifications, form validation, and enhanced UX
 */

// Toast Notification System
class ToastNotification {
    constructor() {
        this.container = this.createContainer();
    }
    
    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }
    
    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${icons[type]}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    }
    
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    }
    
    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }
    
    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
}

// Initialize toast system
const toast = new ToastNotification();
window.toast = toast;

// Password Strength Checker
class PasswordStrength {
    static check(password) {
        let strength = 0;
        const checks = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            numbers: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
        
        // Calculate strength
        Object.values(checks).forEach(check => {
            if (check) strength++;
        });
        
        // Determine level
        let level = 'weak';
        if (strength >= 4) level = 'strong';
        else if (strength >= 3) level = 'medium';
        
        return {
            level,
            strength: (strength / 5) * 100,
            checks
        };
    }
    
    static showIndicator(inputElement, indicatorElement) {
        inputElement.addEventListener('input', function() {
            const result = PasswordStrength.check(this.value);
            
            if (!this.value) {
                indicatorElement.innerHTML = '';
                return;
            }
            
            indicatorElement.innerHTML = `
                <div class="strength-bar">
                    <div class="strength-bar-fill ${result.level}"></div>
                </div>
                <div class="strength-text">
                    Password strength: <strong>${result.level}</strong>
                </div>
            `;
        });
    }
}

// Form Validation Helper
class FormValidator {
    static validateEmail(email) {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(email);
    }
    
    static validateURL(url) {
        try {
            new URL(url.startsWith('http') ? url : 'http://' + url);
            return true;
        } catch {
            return false;
        }
    }
    
    static validateUsername(username) {
        return /^[a-zA-Z0-9_-]{3,50}$/.test(username);
    }
    
    static showError(inputElement, message) {
        inputElement.classList.add('error');
        
        let errorDiv = inputElement.parentElement.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            inputElement.parentElement.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
    }
    
    static clearError(inputElement) {
        inputElement.classList.remove('error');
        const errorDiv = inputElement.parentElement.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    static showSuccess(inputElement) {
        inputElement.classList.remove('error');
        this.clearError(inputElement);
    }
}

// Loading Button State
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
        button.dataset.originalText = button.textContent;
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
    }
}

// Debounce Function
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

// Copy to Clipboard
async function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    try {
        await navigator.clipboard.writeText(text);
        toast.success(successMessage);
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            toast.success(successMessage);
            return true;
        } catch (err) {
            toast.error('Failed to copy to clipboard');
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

// Confirmation Dialog
function confirmAction(message, onConfirm, onCancel = null) {
    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    overlay.innerHTML = `
        <div class="confirm-dialog">
            <div class="confirm-icon">
                <i class="fas fa-question-circle"></i>
            </div>
            <div class="confirm-message">${message}</div>
            <div class="confirm-buttons">
                <button class="btn-confirm-cancel">Cancel</button>
                <button class="btn-confirm-ok">Confirm</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    overlay.querySelector('.btn-confirm-ok').onclick = () => {
        overlay.remove();
        if (onConfirm) onConfirm();
    };
    
    overlay.querySelector('.btn-confirm-cancel').onclick = () => {
        overlay.remove();
        if (onCancel) onCancel();
    };
    
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            overlay.remove();
            if (onCancel) onCancel();
        }
    };
}

// Auto-save Form Data
class AutoSave {
    static save(formId, data) {
        localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    }
    
    static load(formId) {
        const data = localStorage.getItem(`autosave_${formId}`);
        return data ? JSON.parse(data) : null;
    }
    
    static clear(formId) {
        localStorage.removeItem(`autosave_${formId}`);
    }
    
    static enableForForm(formElement) {
        const formId = formElement.id;
        if (!formId) {
            console.error('Form must have an ID for auto-save');
            return;
        }
        
        // Load saved data
        const savedData = this.load(formId);
        if (savedData) {
            Object.keys(savedData).forEach(name => {
                const input = formElement.querySelector(`[name="${name}"]`);
                if (input && input.type !== 'password') {
                    input.value = savedData[name];
                }
            });
        }
        
        // Save on input
        const saveData = debounce(() => {
            const data = {};
            const inputs = formElement.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.name && input.type !== 'password') {
                    data[input.name] = input.value;
                }
            });
            this.save(formId, data);
        }, 1000);
        
        formElement.addEventListener('input', saveData);
        
        // Clear on successful submit
        formElement.addEventListener('submit', () => {
            this.clear(formId);
        });
    }
}

// Export utilities
window.PasswordStrength = PasswordStrength;
window.FormValidator = FormValidator;
window.setButtonLoading = setButtonLoading;
window.debounce = debounce;
window.copyToClipboard = copyToClipboard;
window.confirmAction = confirmAction;
window.AutoSave = AutoSave;

console.log('[TrustLink] UI improvements loaded');

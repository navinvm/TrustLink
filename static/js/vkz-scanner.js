/**
 * TrustLink - VKZ Scanner Functionality
 * Scanning beam animation and result visualization
 */

const scanForm = document.getElementById('scanForm');
const scanBtn = document.getElementById('scanBtn');
const scanningBeam = document.getElementById('scanningBeam');
const urlInput = document.getElementById('urlInput');
const resultsSection = document.getElementById('resultsSection');

// Scan form submission
if (scanForm) {
    scanForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('[TrustLink] Form submitted!');
        
        let url = urlInput.value.trim();
        if (!url) return;
        
        // Auto-format URL: Add https:// if no protocol
        if (!url.match(/^https?:\/\//i)) {
            url = 'https://' + url;
            urlInput.value = url; // Update input field
            console.log('Auto-formatted URL to:', url);
        }
        
        // Track scan start time
        const scanStartTime = Date.now();
        
        // Start scanning animation
        startScanningAnimation();
        
        try {
            // Make API call
            console.log('Sending scan request for:', url);
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                console.error('Server error response:', errorData);
                
                // Handle rate limiting with user-friendly message
                if (response.status === 429) {
                    const retryAfter = errorData.retry_after || 3600;
                    const minutes = Math.ceil(retryAfter / 60);
                    throw new Error(`Rate limit exceeded. Please try again in ${minutes} minutes.`);
                }
                
                throw new Error(errorData.error || `Server returned ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Scan data received:', data);
            
            // Small delay to ensure smooth animation transition (100ms)
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Stop scanning animation
            stopScanningAnimation();
            
            // Calculate scan time
            const scanTime = ((Date.now() - scanStartTime) / 1000).toFixed(2);
            
            // Display results
            displayResults(data, url, scanTime);
            
        } catch (error) {
            console.error('Scan error:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack
            });
            stopScanningAnimation();
            showError('Unable to scan URL. Please try again. Error: ' + error.message);
        }
    });
}

// Start scanning animation with beam effect
function startScanningAnimation() {
    scanBtn.classList.add('scanning');
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing';
    
    // Activate scanning beam
    if (scanningBeam) {
        scanningBeam.style.animation = 'scanning 2s ease-in-out infinite';
    }
    
    urlInput.disabled = true;
    
    // Add analyzing class to search container for glow effect
    const searchContainer = document.querySelector('.vkz-search-container');
    if (searchContainer) {
        searchContainer.style.borderColor = 'rgba(147, 51, 234, 0.5)';
        searchContainer.style.boxShadow = '0 0 40px rgba(147, 51, 234, 0.3)';
    }
}

// Stop scanning animation
function stopScanningAnimation() {
    scanBtn.classList.remove('scanning');
    scanBtn.disabled = false;
    scanBtn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    
    // Stop scanning beam
    if (scanningBeam) {
        scanningBeam.style.animation = 'none';
    }
    
    urlInput.disabled = false;
    
    // Remove analyzing glow
    const searchContainer = document.querySelector('.vkz-search-container');
    if (searchContainer) {
        searchContainer.style.borderColor = '';
        searchContainer.style.boxShadow = '';
    }
}

// Display results with liquid-metal animation
function displayResults(data, url, scanTime) {
    console.log('[TrustLink] displayResults called with:', JSON.stringify(data));
    
    try {
        // Scroll to results
        if (!resultsSection) {
            console.error('resultsSection is null!');
            alert('Error: Results section not found!');
            return;
        }
        
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
        
        const isPhishing = data.prediction === 'Phishing';
        const confidence = Math.round(data.confidence);
        const riskLevel = data.risk_level || data.summary?.risk_level || 'low';
        
        console.log('Parsed data:', { 
            isPhishing, 
            confidence, 
            riskLevel,
            rawRiskLevel: data.risk_level,
            summaryRiskLevel: data.summary?.risk_level
        });
        
        // Update scanned URL
        const scannedUrlEl = document.getElementById('scannedUrl');
        console.log('scannedUrlEl:', scannedUrlEl);
        if (scannedUrlEl) scannedUrlEl.textContent = url;
        
        // Update status badge
        const statusBadge = document.getElementById('statusBadge');
        const statusBadgeText = document.getElementById('statusBadgeText');
        console.log('Badge elements:', { statusBadge, statusBadgeText });
        
        // Update liquid-metal ring with enhanced animations
        const progressCircle = document.getElementById('progressCircle');
        const statusIcon = document.getElementById('statusIcon');
        const statusText = document.getElementById('statusText');
        const confidenceScore = document.getElementById('confidenceScore');
        const verdictTitle = document.getElementById('verdictTitle');
        const verdictMessage = document.getElementById('verdictMessage');
        
        console.log('Ring elements:', {
            progressCircle: !!progressCircle,
            statusIcon: !!statusIcon,
            statusText: !!statusText,
            confidenceScore: !!confidenceScore,
            verdictTitle: !!verdictTitle,
            verdictMessage: !!verdictMessage
        });
        
        // Check if all critical elements exist
        if (!progressCircle || !statusIcon || !statusText || !confidenceScore || !verdictTitle || !verdictMessage) {
            console.error('Missing critical elements!');
            alert('Error: Some display elements are missing. Please refresh the page.');
            return;
        }
    
    // Calculate circle progress (new radius: 85)
    const radius = 85;
    const circumference = 2 * Math.PI * radius;
    const progress = confidence / 100;
    const offset = circumference * (1 - progress);
    
    // Animate liquid-metal progress circle with ultra-smooth easing
    setTimeout(() => {
        if (progressCircle) {
            // Use a very smooth, gradual easing curve
            progressCircle.style.transition = 'stroke-dashoffset 3.5s cubic-bezier(0.16, 1, 0.3, 1), stroke 1.2s cubic-bezier(0.16, 1, 0.3, 1)';
            progressCircle.style.strokeDashoffset = offset;
        }
    }, 400);
    
    // Determine risk level category
    const riskCategory = riskLevel === 'high' ? 'high' : 
                        riskLevel === 'medium' ? 'medium' : 'low';
    
    console.log('Risk category determined:', riskCategory, '(from riskLevel:', riskLevel + ')');
    
    // Risk category takes precedence over prediction for visual display
    if (riskCategory === 'high') {
        // Phishing/Malicious - Red Theme
        updateLiquidGradient('#ef4444', '#dc2626', '#991b1b');
        if (statusIcon) {
            statusIcon.className = 'fas fa-exclamation-triangle vkz-status-icon';
            statusIcon.style.color = '#ef4444';
        }
        if (statusText) {
            statusText.textContent = 'THREAT';
            statusText.style.color = '#ef4444';
        }
        if (confidenceScore) {
            confidenceScore.textContent = confidence + '%';
            confidenceScore.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            confidenceScore.style.webkitBackgroundClip = 'text';
            confidenceScore.style.webkitTextFillColor = 'transparent';
        }
        if (verdictTitle) {
            verdictTitle.textContent = 'Malicious Link Detected';
            verdictTitle.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            verdictTitle.style.webkitBackgroundClip = 'text';
            verdictTitle.style.webkitTextFillColor = 'transparent';
        }
        if (verdictMessage) {
            verdictMessage.textContent = 'This URL has been identified as a phishing attempt. Do not visit this site.';
        }
        
        // Update status badge
        if (statusBadgeText) statusBadgeText.textContent = 'Malicious';
        if (statusBadge) {
            statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
            statusBadge.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            statusBadge.style.color = '#ef4444';
            const statusDot = statusBadge.querySelector('.vkz-status-dot');
            if (statusDot) statusDot.style.background = '#ef4444';
        }
        
        // Update risk level visualization
        updateRiskVisualization('high', confidence);
    } else if (riskCategory === 'medium') {
        // Medium Risk - Yellow/Orange Theme (Caution)
        updateLiquidGradient('#f59e0b', '#f97316', '#ea580c');
        if (statusIcon) {
            statusIcon.className = 'fas fa-exclamation-circle vkz-status-icon';
            statusIcon.style.color = '#f59e0b';
        }
        if (statusText) {
            statusText.textContent = 'CAUTION';
            statusText.style.color = '#f59e0b';
        }
        if (confidenceScore) {
            confidenceScore.textContent = confidence + '%';
            confidenceScore.style.background = 'linear-gradient(135deg, #f59e0b, #f97316)';
            confidenceScore.style.webkitBackgroundClip = 'text';
            confidenceScore.style.webkitTextFillColor = 'transparent';
        }
        if (verdictTitle) {
            verdictTitle.textContent = 'Exercise Caution';
            verdictTitle.style.background = 'linear-gradient(135deg, #f59e0b, #f97316)';
            verdictTitle.style.webkitBackgroundClip = 'text';
            verdictTitle.style.webkitTextFillColor = 'transparent';
        }
        if (verdictMessage) {
            verdictMessage.textContent = 'This URL shows some suspicious indicators. Be cautious when entering this site and verify the legitimacy before sharing sensitive information.';
        }
        
        // Update status badge
        if (statusBadgeText) statusBadgeText.textContent = 'Caution';
        if (statusBadge) {
            statusBadge.style.background = 'rgba(245, 158, 11, 0.1)';
            statusBadge.style.borderColor = 'rgba(245, 158, 11, 0.3)';
            statusBadge.style.color = '#f59e0b';
            const statusDot = statusBadge.querySelector('.vkz-status-dot');
            if (statusDot) statusDot.style.background = '#f59e0b';
        }
        
        // Update risk level visualization
        updateRiskVisualization('medium', confidence);
    } else {
        // Safe - Green/Blue Theme
        updateLiquidGradient('#10b981', '#06b6d4', '#0ea5e9');
        if (statusIcon) {
            statusIcon.className = 'fas fa-shield-check vkz-status-icon';
            statusIcon.style.color = '#10b981';
        }
        if (statusText) {
            statusText.textContent = 'SAFE';
            statusText.style.color = '#10b981';
        }
        if (confidenceScore) {
            confidenceScore.textContent = confidence + '%';
            confidenceScore.style.background = 'linear-gradient(135deg, #10b981, #06b6d4)';
            confidenceScore.style.webkitBackgroundClip = 'text';
            confidenceScore.style.webkitTextFillColor = 'transparent';
        }
        if (verdictTitle) {
            verdictTitle.textContent = 'Link Verified Safe';
            verdictTitle.style.background = 'linear-gradient(135deg, #10b981, #06b6d4)';
            verdictTitle.style.webkitBackgroundClip = 'text';
            verdictTitle.style.webkitTextFillColor = 'transparent';
        }
        if (verdictMessage) {
            verdictMessage.textContent = 'Our AI analysis indicates this URL is legitimate. However, always exercise caution online.';
        }
        
        // Update status badge
        if (statusBadgeText) statusBadgeText.textContent = 'Verified Safe';
        if (statusBadge) {
            statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
            statusBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            statusBadge.style.color = '#10b981';
            const statusDot = statusBadge.querySelector('.vkz-status-dot');
            if (statusDot) statusDot.style.background = '#10b981';
        }
        
        // Update risk level visualization
        updateRiskVisualization('low', confidence);
    }
    
        // Update micro-data cards
        updateMicroCards(data, confidence, riskLevel, scanTime);
        
        // Update additional details
        updateAdditionalDetails(data);
        
        // Trigger micro-interactions
        triggerCardAnimations();
        
        console.log('✅ Display results completed successfully!');
        
        // Add feedback section
        addFeedbackSection(url, data.prediction);
        
    } catch (error) {
        console.error('❌ Error in displayResults:', error);
        console.error('Error stack:', error.stack);
        alert('Display error: ' + error.message);
    }
}

// Update liquid-metal gradient dynamically
function updateLiquidGradient(color1, color2, color3) {
    const gradient = document.getElementById('liquidGradient');
    if (gradient) {
        const stops = gradient.querySelectorAll('stop');
        stops[0].style.stopColor = color1;
        stops[1].style.stopColor = color2;
        stops[2].style.stopColor = color3;
    }
}

// Update micro-cards with data
function updateMicroCards(data, confidence, riskLevel, scanTime) {
    try {
        console.log('Updating micro-cards...');
        
        // Update scan time
        const scanTimeEl = document.getElementById('scanTime');
        if (scanTimeEl && scanTime) {
            scanTimeEl.textContent = scanTime + 's';
        }
        
        // Update detection method
        const detectionMethodEl = document.getElementById('detectionMethod');
        if (detectionMethodEl && data.analysis?.detection_method) {
            const method = data.analysis.detection_method;
            detectionMethodEl.textContent = method === 'whitelist' ? 'Whitelist Match' : 
                                           method === 'ml' ? 'ML Detection' : 'Neural Analysis';
        }
        
        // SSL Status
        const sslStatus = document.getElementById('sslStatus');
        const sslProgress = document.querySelector('[data-card="ssl"] .vkz-progress-bar');
        console.log('SSL elements:', { sslStatus, sslProgress });
        
        if (sslStatus && sslProgress) {
            // Check multiple SSL properties from the response
            const hasSSL = data.security_indicators?.valid_ssl_certificate || 
                          data.details?.has_valid_ssl || 
                          data.has_ssl;
            
            if (hasSSL !== undefined) {
                sslStatus.textContent = hasSSL ? 'Valid' : 'Invalid';
                sslProgress.style.width = hasSSL ? '100%' : '0%';
            } else {
                sslStatus.textContent = 'Unknown';
                sslProgress.style.width = '50%';
            }
        }
        
        // Domain Age
        const domainAge = document.getElementById('domainAge');
        const domainProgress = document.querySelector('[data-card="domain"] .vkz-progress-bar');
        console.log('Domain elements:', { domainAge, domainProgress });
        
        if (domainAge && domainProgress) {
            if (data.domain_reputation && data.domain_reputation.domain_age_readable) {
                domainAge.textContent = data.domain_reputation.domain_age_readable;
                const ageYears = parseInt(data.domain_reputation.domain_age_days) / 365;
                const ageProgress = Math.min(ageYears * 20, 100);
                domainProgress.style.width = ageProgress + '%';
            } else {
                domainAge.textContent = 'Unknown';
                domainProgress.style.width = '30%';
            }
        }
        
        // AI Confidence
        const aiConfidence = document.getElementById('aiConfidence');
        console.log('AI Confidence element:', aiConfidence);
        if (aiConfidence) {
            aiConfidence.textContent = confidence + '%';
        }
        
        // Risk Level
        const riskLevelEl = document.getElementById('riskLevel');
        console.log('Risk Level element:', riskLevelEl);
        if (riskLevelEl) {
            riskLevelEl.textContent = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);
        }
        
        console.log('✅ Micro-cards updated');
    } catch (error) {
        console.error('❌ Error updating micro-cards:', error);
        console.error('Stack:', error.stack);
    }
}

// Update risk visualization bars
function updateRiskVisualization(level, confidence) {
    const riskBars = document.querySelectorAll('.vkz-risk-bar');
    riskBars.forEach(bar => {
        bar.className = 'vkz-risk-bar';
    });
    
    if (level === 'high') {
        riskBars[0].classList.add('vkz-risk-high');
        riskBars[1].classList.add('vkz-risk-high');
        riskBars[2].classList.add('vkz-risk-high');
        if (confidence > 90) {
            riskBars[3].classList.add('vkz-risk-high');
        }
    } else if (level === 'medium') {
        riskBars[0].classList.add('vkz-risk-medium');
        riskBars[1].classList.add('vkz-risk-medium');
    } else {
        riskBars[0].classList.add('vkz-risk-low');
    }
}

// Trigger card stagger animations
function triggerCardAnimations() {
    try {
        console.log('Triggering card animations...');
        const microCards = document.querySelectorAll('.vkz-micro-card');
        console.log('Found micro-cards:', microCards.length);
        
        microCards.forEach((card, index) => {
            // Reset animation
            card.style.animation = 'none';
            setTimeout(() => {
                card.style.animation = '';
            }, 10);
        });
        
        console.log('✅ Card animations triggered');
    } catch (error) {
        console.error('❌ Error triggering animations:', error);
        console.error('Stack:', error.stack);
    }
}

// Enhanced micro-interactions for cards
function enhanceMicroInteractions() {
    const microCards = document.querySelectorAll('.vkz-micro-card');
    
    microCards.forEach(card => {
        // Add ripple effect on click
        card.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.width = '20px';
            ripple.style.height = '20px';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(0, 217, 255, 0.5)';
            ripple.style.transform = 'translate(-50%, -50%) scale(0)';
            ripple.style.animation = 'ripple 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            
            const rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';
            
            this.style.position = 'relative';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// Add ripple animation CSS dynamically
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        to {
            transform: translate(-50%, -50%) scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

// Show error message
function showError(message) {
    alert(message); // TODO: Replace with custom VKZ-styled toast notification
}

// Scan another URL
function scanAnother() {
    resultsSection.style.display = 'none';
    urlInput.value = '';
    urlInput.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// URL input validation and styling
if (urlInput) {
    urlInput.addEventListener('input', (e) => {
        const value = e.target.value.trim();
        
        // Simple URL validation
        const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
        
        if (value && urlPattern.test(value)) {
            urlInput.style.color = 'rgba(16, 185, 129, 0.9)'; // Green tint for valid
        } else if (value) {
            urlInput.style.color = 'rgba(239, 68, 68, 0.9)'; // Red tint for invalid
        } else {
            urlInput.style.color = 'rgba(255, 255, 255, 0.95)'; // Default
        }
    });
    
    // Auto-focus on page load
    window.addEventListener('load', () => {
        setTimeout(() => {
            urlInput.focus();
        }, 500);
    });
}

// Keyboard shortcut: Cmd/Ctrl + K to focus search
document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        urlInput.focus();
        urlInput.select();
    }
});

// Enhanced interactions on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize micro-interactions
    enhanceMicroInteractions();
    
    // Parallax effect on mouse move
    document.addEventListener('mousemove', (e) => {
        const cards = document.querySelectorAll('.vkz-micro-card');
        const x = (e.clientX / window.innerWidth) - 0.5;
        const y = (e.clientY / window.innerHeight) - 0.5;
        
        cards.forEach((card, index) => {
            const speed = (index + 1) * 2;
            card.style.transform = `translateX(${x * speed}px) translateY(${y * speed}px)`;
        });
    });
    
    // Add liquid-metal ring hover glow
    const liquidRing = document.getElementById('liquidRing');
    if (liquidRing) {
        liquidRing.addEventListener('mouseenter', () => {
            const progressCircle = document.getElementById('progressCircle');
            progressCircle.style.filter = 'url(#glow) drop-shadow(0 0 20px currentColor)';
        });
        
        liquidRing.addEventListener('mouseleave', () => {
            const progressCircle = document.getElementById('progressCircle');
            progressCircle.style.filter = 'url(#glow) drop-shadow(0 0 8px currentColor)';
        });
    }
});

// Auto-scan from URL parameter
window.addEventListener('load', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlToScan = urlParams.get('url');
    
    if (urlToScan && urlInput) {
        urlInput.value = urlToScan;
        // Auto-submit after a brief delay
        setTimeout(() => {
            scanForm.dispatchEvent(new Event('submit'));
        }, 500);
    }
});

// Log initialization
console.log('%c🛡️ TrustLink VKZ Scanner Initialized', 'color: #00d9ff; font-size: 14px; font-weight: bold;');
console.log('%cPress Cmd/Ctrl + K to focus scanner', 'color: #9333ea; font-size: 12px;');
console.log('Elements found:', {
    scanForm: !!scanForm,
    scanBtn: !!scanBtn,
    urlInput: !!urlInput,
    resultsSection: !!resultsSection
});

// ========== Feedback Section ==========

// Global variable to store current scan data for feedback
let currentScanData = null;

/**
 * Add feedback section to allow users to rate prediction accuracy
 */
function addFeedbackSection(url, prediction) {
    // Remove existing feedback section if present
    const existingFeedback = document.getElementById('feedbackSection');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Store current scan data
    currentScanData = { url, prediction };
    
    // Create feedback section
    const feedbackSection = document.createElement('div');
    feedbackSection.id = 'feedbackSection';
    feedbackSection.className = 'feedback-section';
    
    feedbackSection.innerHTML = `
        <div class="feedback-header">
            <h3><i class="fas fa-comment-dots"></i> Was this prediction accurate?</h3>
            <p>Your feedback helps improve our detection model!</p>
        </div>
        
        <div class="feedback-buttons">
            <button class="feedback-btn feedback-correct" onclick="submitFeedback('correct')">
                <i class="fas fa-thumbs-up"></i>
                <div class="feedback-content">
                    <strong>Correct</strong>
                    <span>Prediction was accurate</span>
                </div>
            </button>
            
            <button class="feedback-btn feedback-wrong" onclick="submitFeedback('wrong')">
                <i class="fas fa-thumbs-down"></i>
                <div class="feedback-content">
                    <strong>Incorrect</strong>
                    <span>Prediction was wrong</span>
                </div>
            </button>
            
            <button class="feedback-btn feedback-unsure" onclick="submitFeedback('unsure')">
                <i class="fas fa-question-circle"></i>
                <div class="feedback-content">
                    <strong>Not Sure</strong>
                    <span>Need more information</span>
                </div>
            </button>
        </div>
        
        <div class="feedback-response" id="feedbackResponse" style="display: none;"></div>
    `;
    
    // Append to results section
    if (resultsSection) {
        resultsSection.appendChild(feedbackSection);
    }
}

/**
 * Submit user feedback about prediction accuracy
 */
window.submitFeedback = async function(feedbackType) {
    if (!currentScanData) {
        console.error('No scan data available for feedback');
        return;
    }
    
    const { url, prediction } = currentScanData;
    
    // Map feedback type to correct_label for API
    let correctLabel;
    if (feedbackType === 'correct') {
        // Prediction was correct, use same label
        correctLabel = prediction;
    } else if (feedbackType === 'wrong') {
        // Prediction was wrong, flip the label
        correctLabel = prediction === 'Safe' ? 'Phishing' : 'Safe';
    } else {
        // Unsure - keep original prediction but mark as uncertain
        correctLabel = prediction;
    }
    
    const responseDiv = document.getElementById('feedbackResponse');
    responseDiv.style.display = 'block';
    responseDiv.innerHTML = '<p class="feedback-loading"><i class="fas fa-spinner fa-spin"></i> Submitting feedback...</p>';
    
    try {
        const response = await fetch('/api/v1/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                original_prediction: prediction,
                correct_label: correctLabel,
                feedback_type: feedbackType === 'unsure' ? 'unsure' : 'user_report'
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            responseDiv.innerHTML = `
                <div class="feedback-success">
                    <i class="fas fa-check-circle"></i>
                    <strong>Thank you for your feedback!</strong>
                    <p>Your input helps us improve our detection accuracy.</p>
                </div>
            `;
            
            // Disable feedback buttons
            document.querySelectorAll('.feedback-btn').forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.5';
            });
        } else {
            responseDiv.innerHTML = `
                <div class="feedback-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>${result.error || 'Failed to submit feedback'}</strong>
                </div>
            `;
        }
    } catch (error) {
        responseDiv.innerHTML = `
            <div class="feedback-error">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Error submitting feedback</strong>
                <p>Please try again later.</p>
            </div>
        `;
    }
};

/**
 * TrustLink - Frontend JavaScript
 * Handles form submission and result display
 */

console.log('[TrustLink] main.js loaded - v3 - FIXED VERSION');

document.addEventListener('DOMContentLoaded', function() {
    console.log('[TrustLink] DOM Content Loaded');
    
    const scanForm = document.getElementById('scanForm');
    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContainer = document.getElementById('resultsContainer');
    
    console.log('[TrustLink] Elements found:', {
        scanForm: !!scanForm,
        urlInput: !!urlInput,
        analyzeBtn: !!analyzeBtn
    });
    
    if (!scanForm) {
        console.error('[TrustLink] ERROR: scanForm not found!');
        return;
    }
    
    // Form submission handler
    scanForm.addEventListener('submit', async function(e) {
        console.log('[TrustLink] Form submitted!');
        e.preventDefault();
        
        const url = urlInput.value.trim();
        
        if (!url) {
            alert('Please enter a URL to analyze');
            return;
        }
        
        // Show loading overlay
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }
        
        // Show loading, hide results
        loadingIndicator.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        
        try {
            // Send POST request to Flask backend
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            if (!response.ok) {
                // Handle HTTP errors
                let errorMessage = 'Analysis failed';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorData.message || errorMessage;
                } catch (e) {
                    errorMessage = `Server error (${response.status})`;
                }
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            
            if (data.status === 'error') {
                throw new Error(data.error);
            }
            
            // Display results
            displayResults(data);
            
        } catch (error) {
            console.error('[TrustLink] Error during analysis:', error);
            
            // Show user-friendly error message
            const errorContainer = document.getElementById('errorContainer');
            if (errorContainer) {
                errorContainer.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h3>Analysis Failed</h3>
                        <p>${error.message}</p>
                        <button onclick="location.reload()" class="btn-retry">Try Again</button>
                    </div>
                `;
                errorContainer.classList.remove('hidden');
            } else {
                alert('Analysis failed: ' + error.message);
            }
        } finally {
            // Hide loading overlay
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('active');
            }
            
            loadingIndicator.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });
    
    /**
     * Display analysis results in the UI
     */
    function displayResults(data) {
        console.log('[TrustLink] displayResults called with:', data);
        const isPhishing = data.prediction === 'Phishing';
        const confidence = data.confidence;
        
        // Determine risk level based on prediction and confidence
        let riskStatus = 'safe'; // green
        let trafficLightColor = '#00ff00'; // green
        let glowColor = 'rgba(0, 255, 0, 0.5)'; // green glow
        let verdictText = 'Safe';
        let subtitleText = 'URL appears safe to visit';
        
        if (isPhishing) {
            if (confidence >= 70) {
                // High confidence phishing - RED
                riskStatus = 'danger';
                trafficLightColor = '#ff0000';
                glowColor = 'rgba(255, 0, 0, 0.5)';
                verdictText = 'THREAT DETECTED';
                subtitleText = 'High-risk phishing threat identified';
            } else if (confidence >= 50) {
                // Moderate confidence phishing - ORANGE
                riskStatus = 'moderate';
                trafficLightColor = '#ff9900';
                glowColor = 'rgba(255, 153, 0, 0.5)';
                verdictText = 'MODERATE RISK';
                subtitleText = 'Potentially suspicious - proceed with caution';
            } else {
                // Low confidence phishing - ORANGE (uncertain)
                riskStatus = 'moderate';
                trafficLightColor = '#ff9900';
                glowColor = 'rgba(255, 153, 0, 0.5)';
                verdictText = 'UNCERTAIN';
                subtitleText = 'Some suspicious patterns detected';
            }
        } else {
            // Safe prediction - GREEN
            riskStatus = 'safe';
            trafficLightColor = '#00ff00';
            glowColor = 'rgba(0, 255, 0, 0.5)';
            verdictText = 'SAFE';
            subtitleText = 'No threats detected';
        }
        
        // Update Status Shield
        const shieldIcon = document.getElementById('shieldIcon');
        const shieldVerdict = document.getElementById('shieldVerdict');
        const shieldSubtitle = document.getElementById('shieldSubtitle');
        const shieldGlow = document.getElementById('shieldGlow');
        
        // Create traffic light circle
        shieldIcon.className = 'shield-icon ' + riskStatus;
        shieldIcon.innerHTML = `
            <div class="traffic-light" style="
                width: 120px;
                height: 120px;
                border-radius: 50%;
                background: ${trafficLightColor};
                box-shadow: 0 0 40px ${glowColor}, 0 0 80px ${glowColor}, inset 0 0 20px rgba(255, 255, 255, 0.3);
                border: 4px solid rgba(255, 255, 255, 0.2);
                animation: pulse-glow 2s ease-in-out infinite;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 3rem;
            ">
            </div>
        `;
        
        shieldVerdict.textContent = verdictText;
        shieldVerdict.className = 'shield-verdict ' + riskStatus;
        
        shieldSubtitle.textContent = subtitleText;
        
        shieldGlow.style.background = `radial-gradient(circle, ${glowColor}, transparent)`;
        
        // Update Pattern Metrics
        const urlStructure = data.url_structure || {};
        const advanced = data.advanced_metrics || {};
        
        // URL Entropy
        const entropy = advanced.url_entropy || 0;
        document.getElementById('entropyValue').textContent = entropy.toFixed(2);
        document.getElementById('entropyProgress').style.width = Math.min(entropy * 20, 100) + '%';
        
        // Length Score
        const urlLength = urlStructure.url_length || 0;
        const lengthScore = Math.min((urlLength / 200) * 100, 100);
        document.getElementById('lengthValue').textContent = urlLength;
        document.getElementById('lengthProgress').style.width = lengthScore + '%';
        
        // Special Characters
        const specialChars = advanced.num_special_chars || 0;
        const specialScore = Math.min((specialChars / 20) * 100, 100);
        document.getElementById('specialCharsValue').textContent = specialChars;
        document.getElementById('specialCharsProgress').style.width = specialScore + '%';
        
        // Update confidence score
        document.getElementById('confidenceValue').textContent = confidence + '%';
        
        const confidenceProgress = document.getElementById('confidenceProgress');
        confidenceProgress.style.width = confidence + '%';
        
        if (confidence >= 80) {
            confidenceProgress.className = 'confidence-progress-glass high';
        } else if (confidence >= 50) {
            confidenceProgress.className = 'confidence-progress-glass';
        } else {
            confidenceProgress.className = 'confidence-progress-glass danger';
        }
        
        // Check for Zero-Day detection
        const zeroDayAlert = document.getElementById('zeroDayAlert');
        const summary = data.summary || {};
        if (summary.detection_method === 'ML Model' && isPhishing) {
            zeroDayAlert.classList.remove('hidden');
        } else {
            zeroDayAlert.classList.add('hidden');
        }
        
        // Update status badge
        const statusBadge = document.getElementById('statusBadge');
        statusBadge.textContent = riskStatus === 'moderate' ? 'Moderate Risk' : data.prediction;
        statusBadge.className = 'status-badge-glass ' + riskStatus;
        
        // Update risk level
        const riskLevel = document.getElementById('riskLevel');
        riskLevel.textContent = riskStatus === 'moderate' ? 'MODERATE' : data.risk_level.toUpperCase();
        riskLevel.className = 'risk-badge-glass ' + riskStatus;
        
        // Update details list with comprehensive analysis
        const detailsList = document.getElementById('detailsList');
        detailsList.innerHTML = '';
        detailsList.className = 'details-list-glass';
        
        // Detection Method Section
        addSectionHeader(detailsList, 'Detection Method');
        addDetailItem(detailsList, 'Method', summary.detection_method || 'ML Model', 'normal');
        
        if (data.analysis && data.analysis.whitelist_info) {
            addDetailItem(detailsList, 'Whitelist Status', 'Verified Legitimate Domain', 'success');
            addDetailItem(detailsList, 'Reason', data.analysis.whitelist_info.reason, 'normal');
        }
        
        // URL Structure Section
        addSectionHeader(detailsList, 'URL Structure');
        addDetailItem(detailsList, 'Protocol', urlStructure.protocol ? urlStructure.protocol.toUpperCase() : 'Unknown', 'normal');
        addDetailItem(detailsList, 'Domain', urlStructure.domain || 'Unknown', 'normal');
        addDetailItem(detailsList, 'HTTPS Enabled', urlStructure.is_https ? 'Yes' : 'No', urlStructure.is_https ? 'success' : 'danger');
        addDetailItem(detailsList, 'URL Length', urlStructure.url_length + ' characters', 'normal');
        
        // Domain Reputation Section
        addSectionHeader(detailsList, 'Domain Reputation');
        const domainRep = data.domain_reputation || {};
        addDetailItem(detailsList, 'Domain Age', domainRep.domain_age_readable || 'Unknown', domainRep.is_new_domain ? 'warning' : 'success');
        addDetailItem(detailsList, 'New Domain', domainRep.is_new_domain ? 'Yes (< 1 year)' : 'No', domainRep.is_new_domain ? 'warning' : 'success');
        addDetailItem(detailsList, 'Has Registrar', domainRep.has_registrar ? 'Yes' : 'No', domainRep.has_registrar ? 'success' : 'warning');
        addDetailItem(detailsList, 'MX Records', domainRep.has_mx_record ? 'Present' : 'Missing', domainRep.has_mx_record ? 'success' : 'normal');
        
        // Security Indicators Section
        addSectionHeader(detailsList, 'Security Indicators');
        const security = data.security_indicators || {};
        addDetailItem(detailsList, 'Valid SSL', security.valid_ssl_certificate ? 'Yes' : 'No', security.valid_ssl_certificate ? 'success' : 'danger');
        
        if (security.ssl_issuer) {
            addDetailItem(detailsList, 'SSL Issuer', security.ssl_issuer, 'normal');
        }
        
        if (security.ssl_days_until_expiry > 0) {
            addDetailItem(detailsList, 'SSL Expires In', security.ssl_days_until_expiry + ' days', 'normal');
        }
        
        addDetailItem(detailsList, 'IP in URL', security.has_ip_address ? 'Yes' : 'No', security.has_ip_address ? 'warning' : 'success');
        addDetailItem(detailsList, 'Punycode', security.has_punycode ? 'Detected' : 'None', security.has_punycode ? 'warning' : 'success');
        
        // Suspicious Patterns Section
        const suspicious = data.suspicious_patterns || {};
        const suspiciousFound = [];
        
        if (suspicious.ip_address_in_url) suspiciousFound.push('IP Address in URL');
        if (suspicious.suspicious_tld) suspiciousFound.push('Suspicious TLD (.tk, .ml, etc.)');
        if (suspicious.url_shortener) suspiciousFound.push('URL Shortener');
        if (suspicious.login_keywords) suspiciousFound.push('Login Keywords Detected');
        if (suspicious.phishing_keywords_count > 0) suspiciousFound.push(`${suspicious.phishing_keywords_count} Phishing Keywords`);
        if (suspicious.multiple_subdomains) suspiciousFound.push('Multiple Subdomains');
        if (suspicious.hex_encoding) suspiciousFound.push('Hex Encoding');
        if (suspicious.redirect_symbols) suspiciousFound.push('Redirect Symbols');
        
        addSectionHeader(detailsList, 'Suspicious Patterns');
        if (suspiciousFound.length > 0) {
            suspiciousFound.forEach(pattern => {
                addDetailItem(detailsList, '', pattern, 'warning');
            });
        } else {
            addDetailItem(detailsList, '', 'No suspicious patterns detected', 'success');
        }
        
        // Risk Assessment Section
        addSectionHeader(detailsList, 'Risk Assessment');
        const riskAssessment = data.risk_assessment || {};
        addDetailItem(detailsList, 'Risk Factors', riskAssessment.total_risk_indicators || 0, riskAssessment.total_risk_indicators > 0 ? 'warning' : 'success');
        addDetailItem(detailsList, 'Trust Factors', riskAssessment.total_trust_indicators || 0, riskAssessment.total_trust_indicators > 0 ? 'success' : 'normal');
        
        // Risk Factors
        if (riskAssessment.risk_factors && riskAssessment.risk_factors.length > 0) {
            addSectionHeader(detailsList, 'Risk Factors Found');
            riskAssessment.risk_factors.forEach(factor => {
                addDetailItem(detailsList, '', '• ' + factor, 'warning');
            });
        }
        
        // Trust Factors
        if (riskAssessment.trust_factors && riskAssessment.trust_factors.length > 0) {
            addSectionHeader(detailsList, 'Trust Factors Found');
            riskAssessment.trust_factors.forEach(factor => {
                addDetailItem(detailsList, '', '• ' + factor, 'success');
            });
        }
        
        // Advanced Metrics Section (for technical users)
        addSectionHeader(detailsList, 'Advanced Metrics');
        addDetailItem(detailsList, 'Subdomains', advanced.num_subdomains || 0, 'normal');
        addDetailItem(detailsList, 'Dots in URL', advanced.num_dots || 0, 'normal');
        addDetailItem(detailsList, 'Hyphens', advanced.num_hyphens || 0, 'normal');
        addDetailItem(detailsList, 'Digits', advanced.num_digits || 0, 'normal');
        addDetailItem(detailsList, 'Special Char Ratio', (advanced.special_char_ratio || 0).toFixed(4), 'normal');
        addDetailItem(detailsList, 'URL Entropy', (advanced.url_entropy || 0).toFixed(2), 'normal');
        
        // Add feedback section
        addFeedbackSection(data);
        
        // Show results container
        resultsContainer.classList.remove('hidden');
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Make displayResults globally accessible for debugging
    window.displayResults = displayResults;
    console.log('[TrustLink] displayResults function is now globally available');
    
    /**
     * Add feedback section to allow users to report incorrect predictions
     */
    function addFeedbackSection(data) {
        // Remove existing feedback section if present
        const existingFeedback = document.getElementById('feedbackSection');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        const detailsList = document.getElementById('detailsList');
        
        // Create feedback section
        const feedbackSection = document.createElement('div');
        feedbackSection.id = 'feedbackSection';
        feedbackSection.className = 'feedback-section';
        
        feedbackSection.innerHTML = `
            <div class="feedback-header">
                <h3>Help Improve Our AI</h3>
                <p>Was this prediction accurate? Your feedback helps train the model!</p>
            </div>
            
            <div class="feedback-buttons">
                <button class="feedback-btn feedback-correct" onclick="window.submitFeedback('correct')">
                    <span class="feedback-icon"></span>
                    <div class="feedback-content">
                        <strong>Correct</strong>
                        <small>Prediction was accurate</small>
                    </div>
                </button>
                
                <button class="feedback-btn feedback-wrong" onclick="window.submitFeedback('wrong')">
                    <span class="feedback-icon"></span>
                    <div class="feedback-content">
                        <strong>Incorrect</strong>
                        <small>Prediction was wrong</small>
                    </div>
                </button>
                
                <button class="feedback-btn feedback-unsure" onclick="window.submitFeedback('unsure')">
                    <span class="feedback-icon"></span>
                    <div class="feedback-content">
                        <strong>Not Sure</strong>
                        <small>Need more information</small>
                    </div>
                </button>
            </div>
            
            <div class="feedback-response" id="feedbackResponse" style="display: none;"></div>
        `;
        
        // Store current scan data globally for feedback
        window.currentScanData = {
            url: data.url,
            prediction: data.prediction,
            confidence: data.confidence,
            risk_level: data.risk_level
        };
        
        // Insert after results container
        resultsContainer.appendChild(feedbackSection);
    }
    
    /**
     * Submit user feedback about prediction accuracy
     */
    window.submitFeedback = async function(feedbackType) {
        const scanData = window.currentScanData;
        if (!scanData) {
            alert('No scan data available');
            return;
        }
        
        // Determine correct label
        let correctLabel;
        let feedbackTypeStr;
        
        if (feedbackType === 'correct') {
            correctLabel = scanData.prediction;
            feedbackTypeStr = 'positive';
        } else if (feedbackType === 'wrong') {
            correctLabel = scanData.prediction === 'Phishing' ? 'Safe' : 'Phishing';
            feedbackTypeStr = 'correction';
        } else {
            correctLabel = 'Unsure';
            feedbackTypeStr = 'unsure';
        }
        
        // Show loading
        const responseDiv = document.getElementById('feedbackResponse');
        responseDiv.style.display = 'block';
        responseDiv.innerHTML = '<p class="feedback-loading">⏳ Submitting feedback...</p>';
        
        try {
            const response = await fetch('/api/v1/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: scanData.url,
                    original_prediction: scanData.prediction,
                    correct_label: correctLabel,
                    feedback_type: feedbackTypeStr
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                responseDiv.innerHTML = `
                    <div class="feedback-success">
                        <strong>Thank you for your feedback!</strong>
                        <p>Your input will help improve the AI model for everyone.</p>
                    </div>
                `;
                
                // Disable feedback buttons
                document.querySelectorAll('.feedback-btn').forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.6';
                    btn.style.cursor = 'not-allowed';
                });
            } else {
                responseDiv.innerHTML = `
                    <div class="feedback-error">
                        <strong>${result.error || 'Failed to submit feedback'}</strong>
                        <p>Please try again or contact support.</p>
                    </div>
                `;
            }
        } catch (error) {
            responseDiv.innerHTML = `
                <div class="feedback-error">
                    <strong>Error submitting feedback</strong>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }
    
    /**
     * Helper function to add a section header
     */
    function addSectionHeader(listElement, title) {
        const li = document.createElement('li');
        li.className = 'section-header';
        li.textContent = title;
        listElement.appendChild(li);
    }
    
    /**
     * Helper function to add a detail item to the list
     */
    function addDetailItem(listElement, label, value, type) {
        const li = document.createElement('li');
        li.className = 'detail-item';
        
        if (label) {
            const labelSpan = document.createElement('span');
            labelSpan.className = 'detail-label';
            labelSpan.textContent = label + ':';
            li.appendChild(labelSpan);
        }
        
        const valueSpan = document.createElement('span');
        valueSpan.className = 'detail-value ' + type;
        valueSpan.textContent = value;
        
        li.appendChild(valueSpan);
        listElement.appendChild(li);
    }
});

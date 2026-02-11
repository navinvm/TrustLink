/**
 * TrustLink Complete Animation - Fresh Implementation
 * Based on the 45-60 second animation prompt
 */

console.log('%c🎬 TrustLink Animation Ready', 'color: #00D2FF; font-size: 16px; font-weight: bold;');

// Initialize animation HTML but don't start it
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM Ready - Animation waiting for trigger');
    
    const container = document.getElementById('heroAnimationContent');
    
    if (!container) {
        console.error('❌ Animation container not found!');
        return;
    }
    
    console.log('✅ Container found');
    
    // Insert the animation HTML but hidden
    container.innerHTML = getFullAnimationHTML();
    container.style.display = 'none'; // Hide initially
    
    console.log('✅ Animation HTML loaded (hidden)');
});

// Function to start animation (called by URL analysis)
window.startTrustLinkAnimation = function() {
    const container = document.getElementById('heroAnimationContent');
    
    if (!container) {
        console.error('❌ Animation container not found!');
        return;
    }
    
    // Show the animation
    container.style.display = 'block';
    
    console.log('🎮 Starting Animation...');
    
    if (typeof HeroAnimationController === 'undefined') {
        console.warn('⚠️ HeroAnimationController not ready, retrying...');
        setTimeout(window.startTrustLinkAnimation, 500);
        return;
    }
    
    try {
        // Stop any existing animation
        if (window.trustLinkAnimation) {
            window.trustLinkAnimation.pause();
        }
        
        // Start new animation
        window.trustLinkAnimation = new HeroAnimationController();
        console.log('%c✅ ANIMATION STARTED!', 'color: #39FF14; font-size: 14px; font-weight: bold;');
        
        // Auto-hide after one complete loop (5 seconds)
        setTimeout(function() {
            if (window.trustLinkAnimation) {
                window.trustLinkAnimation.pause();
            }
            container.style.display = 'none';
            console.log('✅ Animation complete - hidden');
        }, 5000);
    } catch (error) {
        console.error('❌ Error starting animation:', error);
    }
}

function getFullAnimationHTML() {
    return `
<section class="hero-animation-section">
    <div class="animation-container" id="animationContainer">
        
        <!-- SCENE 1: Incoming Threat -->
        <div class="animation-scene scene-1 active" id="scene1">
            <div class="scene-content">
                <div class="threat-incoming">
                    <div class="threat-visual">
                        <div class="danger-circle">
                            <i class="fas fa-skull-crossbones"></i>
                        </div>
                        <div class="warning-waves"></div>
                    </div>
                    <h1 class="threat-title">INCOMING PHISHING ATTEMPT</h1>
                    <div class="threat-url-box">
                        <div class="url-header">Suspicious URL Detected</div>
                        <div class="url-display">
                            <i class="fas fa-globe"></i>
                            <span>secure-bank-verify.com/login</span>
                        </div>
                    </div>
                    <div class="threat-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Analyzing Threat Level...</span>
                    </div>
                </div>
            </div>
            <div class="scene-text">Threat Detected</div>
        </div>

        <!-- SCENE 2: TrustLink Activation -->
        <div class="animation-scene scene-2" id="scene2">
            <div class="scene-content">
                <div class="activation-display">
                    <div class="logo-activation">
                        <img src="/static/images/TrustLinkLogo.png" alt="TrustLink" class="activating-logo">
                        <div class="scan-ring"></div>
                        <div class="scan-ring ring-2"></div>
                    </div>
                    <h2 class="activation-text">TrustLink Analyzing...</h2>
                    <div class="scan-progress">
                        <div class="progress-fill-animated"></div>
                    </div>
                </div>
            </div>
            <div class="scene-text">AI Scanning Active</div>
        </div>

        <!-- SCENE 3: Pattern Analysis -->
        <div class="animation-scene scene-3" id="scene3">
            <div class="scene-content">
                <div class="pattern-analysis-display">
                    <h2 class="analysis-header">
                        <i class="fas fa-brain"></i>
                        Deep Pattern Analysis
                    </h2>
                    <div class="analysis-grid">
                        <div class="analysis-card">
                            <div class="card-icon red">
                                <i class="fas fa-exclamation-triangle"></i>
                            </div>
                            <div class="card-content">
                                <h3>Suspicious Structure</h3>
                                <p>87% Match</p>
                            </div>
                        </div>
                        <div class="analysis-card">
                            <div class="card-icon red">
                                <i class="fas fa-user-secret"></i>
                            </div>
                            <div class="card-content">
                                <h3>Phishing Patterns</h3>
                                <p>92% Match</p>
                            </div>
                        </div>
                        <div class="analysis-card">
                            <div class="card-icon red">
                                <i class="fas fa-link"></i>
                            </div>
                            <div class="card-content">
                                <h3>Malicious Redirect</h3>
                                <p>95% Match</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="scene-text">Pattern Recognition Complete</div>
        </div>

        <!-- SCENE 4: AI Detection Result -->
        <div class="animation-scene scene-4" id="scene4">
            <div class="scene-content">
                <div class="detection-result">
                    <div class="result-icon danger">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="result-verdict">
                        <h2 class="verdict-title">PHISHING DETECTED</h2>
                        <p class="verdict-subtitle">AI Pattern Recognition</p>
                    </div>
                    <div class="threat-indicators">
                        <div class="indicator">
                            <i class="fas fa-shield-alt"></i>
                            <span>Zero-Day Protection</span>
                        </div>
                        <div class="indicator">
                            <i class="fas fa-brain"></i>
                            <span>ML Analysis</span>
                        </div>
                        <div class="indicator">
                            <i class="fas fa-bolt"></i>
                            <span>Real-Time Scan</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="scene-text">AI-Powered Threat Detection</div>
        </div>

        <!-- SCENE 5: Threat Blocked - Complete -->
        <div class="animation-scene scene-5" id="scene5">
            <div class="scene-content">
                <div class="completion-display">
                    <div class="success-shield">
                        <i class="fas fa-shield-check"></i>
                    </div>
                    <h1 class="completion-title">THREAT BLOCKED</h1>
                    <p class="completion-subtitle">You are protected by TrustLink AI</p>
                    <div class="protection-stats">
                        <div class="stat">
                            <div class="stat-number">100%</div>
                            <div class="stat-label">Protected</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">0.8s</div>
                            <div class="stat-label">Detection Time</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">AI</div>
                            <div class="stat-label">Powered</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="scene-text">Analysis Complete</div>
        </div>

    </div>
</section>
    `;
}

console.log('? Animation module loaded');

/**
 * Simple Animation Trigger - Guaranteed to Work
 */

console.log('?? Animation module loading...');

// Store animation HTML
let animationHTML = null;
let animationActive = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('? DOM Ready');
    
    // Get the animation container
    const container = document.getElementById('heroAnimationContent');
    if (!container) {
        console.error('? No animation container found');
        return;
    }
    
    // Hide it initially
    container.style.display = 'none';
    console.log('? Animation container hidden and ready');
    
    // Find the analyze button/form
    const scanForm = document.getElementById('scanForm');
    if (!scanForm) {
        console.error('? No scan form found');
        return;
    }
    
    console.log('? Scan form found');
    
    // Add click listener to analyze button FIRST (before other handlers)
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            console.log('?? Analyze clicked - checking if animation should play');
            const urlInput = document.getElementById('urlInput');
            if (urlInput && urlInput.value.trim()) {
                console.log('?? URL present - triggering animation!');
                playAnimation();
            }
        }, true); // Use capture phase to run FIRST
    }
});

function playAnimation() {
    const container = document.getElementById('heroAnimationContent');
    if (!container) return;
    
    console.log('?? Playing animation...');
    
    // Show container
    container.style.display = 'block';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100vw';
    container.style.height = '100vh';
    container.style.zIndex = '9999';
    
    // Load animation if not loaded
    if (!container.innerHTML || container.innerHTML.trim() === '') {
        container.innerHTML = getAnimationHTML();
        console.log('? Animation HTML loaded');
    }
    
    // Start animation controller
    setTimeout(function() {
        if (typeof HeroAnimationController !== 'undefined') {
            if (window.animationController) {
                window.animationController.pause();
            }
            window.animationController = new HeroAnimationController();
            console.log('? Animation playing!');
            
            // Hide after 5 seconds
            setTimeout(function() {
                container.style.display = 'none';
                if (window.animationController) {
                    window.animationController.pause();
                }
                console.log('? Animation hidden');
            }, 5000);
        } else {
            console.error('? HeroAnimationController not found');
        }
    }, 100);
}

function getAnimationHTML() {
    return `
<section class="hero-animation-section">
    <div class="animation-container" id="animationContainer">
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
                </div>
            </div>
            <div class="scene-text">Threat Detected</div>
        </div>
        <div class="animation-scene scene-2" id="scene2">
            <div class="scene-content">
                <div class="activation-display">
                    <div class="logo-activation">
                        <img src="/static/images/TrustLinkLogo.png" alt="TrustLink" class="activating-logo">
                        <div class="scan-ring"></div>
                        <div class="scan-ring ring-2"></div>
                    </div>
                    <h2 class="activation-text">TrustLink Analyzing...</h2>
                </div>
            </div>
            <div class="scene-text">AI Scanning Active</div>
        </div>
        <div class="animation-scene scene-3" id="scene3">
            <div class="scene-content">
                <div class="pattern-analysis-display">
                    <h2 class="analysis-header"><i class="fas fa-brain"></i> Deep Pattern Analysis</h2>
                    <div class="analysis-grid">
                        <div class="analysis-card">
                            <div class="card-icon red"><i class="fas fa-exclamation-triangle"></i></div>
                            <div class="card-content"><h3>Suspicious Structure</h3><p>87% Match</p></div>
                        </div>
                        <div class="analysis-card">
                            <div class="card-icon red"><i class="fas fa-user-secret"></i></div>
                            <div class="card-content"><h3>Phishing Patterns</h3><p>92% Match</p></div>
                        </div>
                        <div class="analysis-card">
                            <div class="card-icon red"><i class="fas fa-link"></i></div>
                            <div class="card-content"><h3>Malicious Redirect</h3><p>95% Match</p></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="scene-text">Pattern Recognition Complete</div>
        </div>
        <div class="animation-scene scene-4" id="scene4">
            <div class="scene-content">
                <div class="detection-result">
                    <div class="result-icon danger"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="result-verdict">
                        <h2 class="verdict-title">PHISHING DETECTED</h2>
                        <p class="verdict-subtitle">AI Pattern Recognition</p>
                    </div>
                </div>
            </div>
            <div class="scene-text">AI-Powered Threat Detection</div>
        </div>
        <div class="animation-scene scene-5" id="scene5">
            <div class="scene-content">
                <div class="completion-display">
                    <div class="success-shield"><i class="fas fa-shield-check"></i></div>
                    <h1 class="completion-title">THREAT BLOCKED</h1>
                    <p class="completion-subtitle">You are protected by TrustLink AI</p>
                </div>
            </div>
            <div class="scene-text">Analysis Complete</div>
        </div>
    </div>
</section>
    `;
}

console.log('? Animation module ready');

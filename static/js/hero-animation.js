/**
 * TrustLink Hero Animation Controller
 * Manages the 45-60 second animation timeline
 */

class HeroAnimationController {
    constructor() {
        this.currentScene = 0;
        this.totalScenes = 5;
        this.isPlaying = true;
        this.animationTimer = null;
        this.progressInterval = null;
        
        // Scene durations in milliseconds - FAST 5 second animation
        this.sceneDurations = [
            1000,   // Scene 1: The Problem (1s)
            1000,   // Scene 2: TrustLink Solution (1s)
            1000,   // Scene 3: AI Analysis (1s)
            1000,   // Scene 4: Defense & Result (1s)
            1000    // Scene 5: Tech Stack & CTA (1s)
        ];
        
        this.totalDuration = this.sceneDurations.reduce((a, b) => a + b, 0);
        this.currentTime = 0;
        
        this.init();
    }
    
    init() {
        // Get DOM elements
        this.scenes = document.querySelectorAll('.animation-scene');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.replayBtn = document.getElementById('replayBtn');
        this.progressFill = document.getElementById('progressFill');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start the animation
        this.startAnimation();
        
        // Add audio support (optional)
        this.setupAudio();
    }
    
    setupEventListeners() {
        // Play/Pause button
        this.playPauseBtn.addEventListener('click', () => {
            if (this.isPlaying) {
                this.pause();
            } else {
                this.play();
            }
        });
        
        // Replay button
        this.replayBtn.addEventListener('click', () => {
            this.replay();
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                if (this.isPlaying) {
                    this.pause();
                } else {
                    this.play();
                }
            } else if (e.code === 'ArrowRight') {
                this.nextScene();
            } else if (e.code === 'ArrowLeft') {
                this.previousScene();
            } else if (e.code === 'KeyR') {
                this.replay();
            }
        });
        
        // Click on scene to pause
        this.scenes.forEach(scene => {
            scene.addEventListener('click', () => {
                if (this.isPlaying) {
                    this.pause();
                } else {
                    this.play();
                }
            });
        });
    }
    
    setupAudio() {
        // Audio effects (optional - can be added later)
        this.sounds = {
            scan: null,
            alert: null,
            success: null,
            danger: null
        };
        
        // Uncomment to add sound effects
        // this.sounds.scan = new Audio('/static/audio/scan.mp3');
        // this.sounds.alert = new Audio('/static/audio/alert.mp3');
        // this.sounds.success = new Audio('/static/audio/success.mp3');
        // this.sounds.danger = new Audio('/static/audio/danger.mp3');
    }
    
    playSound(soundName) {
        if (this.sounds[soundName] && this.sounds[soundName].readyState >= 2) {
            this.sounds[soundName].currentTime = 0;
            this.sounds[soundName].play().catch(e => console.log('Audio play failed:', e));
        }
    }
    
    startAnimation() {
        this.showScene(0);
        this.scheduleNextScene();
        this.startProgressBar();
    }
    
    showScene(index) {
        // Hide all scenes
        this.scenes.forEach(scene => {
            scene.classList.remove('active');
        });
        
        // Show current scene
        if (index >= 0 && index < this.totalScenes) {
            this.scenes[index].classList.add('active');
            this.currentScene = index;
            
            // Trigger scene-specific actions
            this.onSceneChange(index);
        }
    }
    
    onSceneChange(sceneIndex) {
        console.log(`Scene ${sceneIndex + 1} activated`);
        
        // Play scene-specific sounds
        switch(sceneIndex) {
            case 0: // The Problem
                // No sound or subtle ambient
                break;
            case 1: // TrustLink Solution
                this.playSound('scan');
                break;
            case 2: // AI Analysis
                this.playSound('scan');
                break;
            case 3: // Defense & Result
                this.playSound('danger');
                setTimeout(() => this.playSound('success'), 2000);
                break;
            case 4: // Tech Stack & CTA
                // Completion sound
                break;
        }
    }
    
    scheduleNextScene() {
        if (!this.isPlaying) return;
        
        const currentDuration = this.sceneDurations[this.currentScene];
        
        this.animationTimer = setTimeout(() => {
            if (this.currentScene < this.totalScenes - 1) {
                this.showScene(this.currentScene + 1);
                this.scheduleNextScene();
            } else {
                // Animation complete - loop or stop
                this.onAnimationComplete();
            }
        }, currentDuration);
    }
    
    onAnimationComplete() {
        console.log('Animation complete');
        this.isPlaying = false;
        this.updatePlayPauseButton();
        
        // Auto-replay after 3 seconds
        setTimeout(() => {
            this.replay();
        }, 3000);
    }
    
    startProgressBar() {
        this.progressInterval = setInterval(() => {
            if (this.isPlaying) {
                this.currentTime += 100; // Update every 100ms
                const progress = (this.currentTime / this.totalDuration) * 100;
                this.progressFill.style.width = Math.min(progress, 100) + '%';
                
                if (progress >= 100) {
                    this.currentTime = 0;
                }
            }
        }, 100);
    }
    
    play() {
        this.isPlaying = true;
        this.scheduleNextScene();
        this.updatePlayPauseButton();
    }
    
    pause() {
        this.isPlaying = false;
        if (this.animationTimer) {
            clearTimeout(this.animationTimer);
        }
        this.updatePlayPauseButton();
    }
    
    replay() {
        this.pause();
        this.currentTime = 0;
        this.progressFill.style.width = '0%';
        this.currentScene = 0;
        this.showScene(0);
        setTimeout(() => {
            this.isPlaying = true;
            this.scheduleNextScene();
            this.updatePlayPauseButton();
        }, 100);
    }
    
    nextScene() {
        this.pause();
        if (this.currentScene < this.totalScenes - 1) {
            this.showScene(this.currentScene + 1);
        }
    }
    
    previousScene() {
        this.pause();
        if (this.currentScene > 0) {
            this.showScene(this.currentScene - 1);
        }
    }
    
    updatePlayPauseButton() {
        const icon = this.playPauseBtn.querySelector('i');
        if (this.isPlaying) {
            icon.className = 'fas fa-pause';
        } else {
            icon.className = 'fas fa-play';
        }
    }
}

// Initialize animation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const animation = new HeroAnimationController();
    
    // Make it globally accessible for debugging
    window.heroAnimation = animation;
    
    console.log('TrustLink Hero Animation initialized');
    console.log('Controls: Space = Play/Pause, Arrow Keys = Navigate, R = Replay');
});

// Add smooth scroll to main content after animation
document.addEventListener('DOMContentLoaded', () => {
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        // Auto-scroll hint after first loop
        setTimeout(() => {
            const scrollHint = document.createElement('div');
            scrollHint.className = 'scroll-hint';
            scrollHint.innerHTML = '<i class="fas fa-chevron-down"></i><span>Scroll to explore</span>';
            scrollHint.style.cssText = `
                position: fixed;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                color: var(--accent-cyan);
                text-align: center;
                animation: bounce 2s ease-in-out infinite;
                cursor: pointer;
                z-index: 50;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
            `;
            
            scrollHint.addEventListener('click', () => {
                mainContent.scrollIntoView({ behavior: 'smooth' });
                scrollHint.remove();
            });
            
            document.body.appendChild(scrollHint);
            
            // Add bounce animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes bounce {
                    0%, 100% { transform: translate(-50%, 0); }
                    50% { transform: translate(-50%, -10px); }
                }
            `;
            document.head.appendChild(style);
        }, 65000); // After first complete cycle
    }
});

// Performance optimization: Pause animation when tab is not visible
document.addEventListener('visibilitychange', () => {
    if (window.heroAnimation) {
        if (document.hidden) {
            window.heroAnimation.pause();
        } else {
            window.heroAnimation.play();
        }
    }
});

// Add touch support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    if (window.heroAnimation) {
        if (touchEndX < touchStartX - 50) {
            // Swipe left - next scene
            window.heroAnimation.nextScene();
        }
        if (touchEndX > touchStartX + 50) {
            // Swipe right - previous scene
            window.heroAnimation.previousScene();
        }
    }
}

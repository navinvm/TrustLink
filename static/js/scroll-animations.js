/**
 * TrustLink Scroll Animations
 * Reveals elements as they scroll into view
 */

(function() {
    'use strict';

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
        console.log('[TrustLink] Reduced motion preference detected - animations disabled');
        return;
    }

    /**
     * Intersection Observer for scroll-triggered animations
     */
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -100px 0px', // Trigger slightly before element enters viewport
        threshold: [0, 0.1, 0.3, 0.5]
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add revealed class when element enters viewport
                entry.target.classList.add('revealed');
                
                // Optional: Stop observing after reveal (one-time animation)
                // observer.unobserve(entry.target);
            } else {
                // Optional: Remove class when scrolling back up (repeating animation)
                // entry.target.classList.remove('revealed');
            }
        });
    }, observerOptions);

    /**
     * Initialize scroll animations on page load
     */
    function initScrollAnimations() {
        // Find all elements with scroll-reveal class
        const scrollElements = document.querySelectorAll('.scroll-reveal');
        
        scrollElements.forEach(element => {
            observer.observe(element);
        });

        console.log(`[TrustLink] Scroll animations initialized for ${scrollElements.length} elements`);
    }

    /**
     * Add scroll animations to dynamically loaded content
     */
    function observeNewElements(elements) {
        if (!elements) return;
        
        const elementsArray = Array.isArray(elements) ? elements : [elements];
        
        elementsArray.forEach(element => {
            if (element.classList.contains('scroll-reveal')) {
                observer.observe(element);
            }
            
            // Also observe children with scroll-reveal class
            const children = element.querySelectorAll('.scroll-reveal');
            children.forEach(child => observer.observe(child));
        });
    }

    /**
     * Parallax effect for background elements
     */
    function initParallax() {
        const parallaxElements = document.querySelectorAll('.parallax');
        
        if (parallaxElements.length === 0) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        }, { passive: true });

        console.log(`[TrustLink] Parallax initialized for ${parallaxElements.length} elements`);
    }

    /**
     * Animate numbers on scroll (count-up effect)
     */
    function animateNumbers() {
        const numberElements = document.querySelectorAll('.count-up');
        
        numberElements.forEach(element => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !element.dataset.animated) {
                        element.dataset.animated = 'true';
                        animateNumber(element);
                        observer.unobserve(element);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(element);
        });
    }

    /**
     * Animate a number element from 0 to its final value
     */
    function animateNumber(element) {
        const text = element.textContent.trim();
        const hasPlus = text.includes('+');
        const hasLessThan = text.includes('<');
        const hasPercent = text.includes('%');
        
        // Special case: Don't animate "24/7" - just show it as is
        if (text === '24/7') {
            element.dataset.animated = 'true';
            return;
        }
        
        // Extract number (only digits before any slash)
        let numberText = text.split('/')[0]; // Get part before slash
        let number = parseFloat(numberText.replace(/[^\d.]/g, ''));
        
        if (isNaN(number)) return;

        const duration = 2000; // 2 seconds
        const steps = 60;
        const stepDuration = duration / steps;
        const increment = number / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            
            if (current >= number) {
                current = number;
                clearInterval(timer);
            }

            // Format the number
            let displayValue = Math.floor(current);
            
            // Handle decimals for small numbers
            if (number < 10) {
                displayValue = current.toFixed(1);
            }

            // Add symbols back
            let formatted = displayValue.toString();
            if (hasLessThan) formatted = '<' + formatted;
            if (hasPlus) formatted += '+';
            if (hasPercent) formatted += '%';
            if (text.includes('M')) formatted += 'M';
            if (text.includes('K')) formatted += 'K';
            if (text.includes('s')) formatted += 's';
            if (text.includes('/')) {
                const parts = text.split('/');
                if (parts.length > 1) formatted += '/' + parts[1];
            }

            element.textContent = formatted;
        }, stepDuration);
    }

    /**
     * Stagger animation delays for child elements
     */
    function applyStaggerDelay(container, childSelector, baseDelay = 100) {
        const children = container.querySelectorAll(childSelector);
        
        children.forEach((child, index) => {
            child.style.animationDelay = `${index * baseDelay}ms`;
        });
    }

    /**
     * Add hover glow effect to elements
     */
    function initHoverEffects() {
        const glowElements = document.querySelectorAll('.hover-glow');
        
        glowElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.style.transition = 'text-shadow 0.3s ease';
            });
        });
    }

    /**
     * Initialize all animations
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initScrollAnimations();
                initParallax();
                animateNumbers();
                initHoverEffects();
            });
        } else {
            initScrollAnimations();
            initParallax();
            animateNumbers();
            initHoverEffects();
        }
    }

    // Initialize
    init();

    // Export functions for external use
    window.TrustLinkAnimations = {
        observeNewElements,
        applyStaggerDelay,
        animateNumber
    };

    console.log('%c🎨 TrustLink Scroll Animations Loaded', 'color: #00d9ff; font-size: 12px; font-weight: bold;');

})();

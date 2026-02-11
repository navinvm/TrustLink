/**
 * TrustLink - Mobile Menu Handler
 * Handles mobile navigation toggle and interactions
 */

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileMenu);
    } else {
        initMobileMenu();
    }
    
    function initMobileMenu() {
        const menuToggle = document.getElementById('mobileMenuToggle');
        const mobileNav = document.getElementById('mobileNav');
        
        if (!menuToggle || !mobileNav) {
            return; // Elements not found
        }
        
        // Toggle menu on button click
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMenu();
        });
        
        // Close menu when clicking nav links
        const navLinks = mobileNav.querySelectorAll('.nav-link, .logout-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeMenu();
                }
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!mobileNav.contains(e.target) && !menuToggle.contains(e.target)) {
                    closeMenu();
                }
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && mobileNav.classList.contains('active')) {
                closeMenu();
                menuToggle.focus();
            }
        });
        
        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth > 768) {
                    closeMenu();
                }
            }, 250);
        });
        
        // Toggle menu function
        function toggleMenu() {
            const isActive = mobileNav.classList.contains('active');
            
            if (isActive) {
                closeMenu();
            } else {
                openMenu();
            }
        }
        
        // Open menu
        function openMenu() {
            mobileNav.classList.add('active');
            menuToggle.setAttribute('aria-expanded', 'true');
            
            // Change icon to X
            const icon = menuToggle.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            }
            
            // Prevent body scroll on mobile
            if (window.innerWidth <= 768) {
                document.body.style.overflow = 'hidden';
            }
            
            // Focus first nav link
            const firstLink = mobileNav.querySelector('.nav-link');
            if (firstLink) {
                setTimeout(() => firstLink.focus(), 100);
            }
        }
        
        // Close menu
        function closeMenu() {
            mobileNav.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
            
            // Change icon back to bars
            const icon = menuToggle.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
        
        // Add smooth scroll behavior for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#') {
                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        closeMenu();
                        
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                        
                        // Update URL without jumping
                        history.pushState(null, null, href);
                    }
                }
            });
        });
        
        console.log('[TrustLink] Mobile menu initialized');
    }
})();

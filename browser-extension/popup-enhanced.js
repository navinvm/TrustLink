/**
 * TrustLink Browser Extension - Enhanced UX Features
 * Additional functionality for improved user experience
 */

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
    <span style="margin-left: 8px;">${message}</span>
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Enhanced safe mode toggle with feedback
const safeModeToggle = document.getElementById('safeModeToggle');
const safeModeStatus = document.getElementById('safeModeStatus');
const safeModeStatusText = document.getElementById('safeModeStatusText');

if (safeModeToggle) {
  safeModeToggle.addEventListener('change', async function() {
    const enabled = this.checked;
    
    // Save to storage
    await chrome.storage.local.set({ safeMode: enabled });
    
    // Show feedback
    safeModeStatus.style.display = 'block';
    safeModeStatusText.textContent = enabled 
      ? 'Safe Mode enabled - Malicious sites will be blocked automatically' 
      : 'Safe Mode disabled - You will receive warnings only';
    
    showToast(
      enabled ? 'Safe Mode Enabled' : 'Safe Mode Disabled',
      enabled ? 'success' : 'warning'
    );
    
    // Auto-hide status after 3 seconds
    setTimeout(() => {
      safeModeStatus.style.display = 'none';
    }, 3000);
  });
  
  // Load initial state
  chrome.storage.local.get(['safeMode'], function(result) {
    safeModeToggle.checked = result.safeMode || false;
  });
}

// Enhanced dropdown toggle with smooth animation
const flaggedToggle = document.getElementById('flaggedToggle');
const flaggedContent = document.getElementById('flaggedContent');

if (flaggedToggle && flaggedContent) {
  flaggedToggle.addEventListener('click', function() {
    const isOpen = flaggedContent.style.display === 'block';
    
    if (isOpen) {
      flaggedContent.style.display = 'none';
      this.classList.remove('active');
    } else {
      flaggedContent.style.display = 'block';
      this.classList.add('active');
    }
  });
}

// Enhanced clear cache with confirmation
const clearCacheBtn = document.getElementById('clearCacheBtn');
if (clearCacheBtn) {
  clearCacheBtn.addEventListener('click', async function() {
    const confirmed = confirm('Are you sure you want to clear the cache? This will remove all cached scan results.');
    
    if (confirmed) {
      try {
        // Show loading state
        const originalHTML = this.innerHTML;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
        this.disabled = true;
        
        // Clear cache
        await chrome.runtime.sendMessage({ action: 'clearCache' });
        
        // Update UI
        document.getElementById('cacheSize').textContent = '0';
        
        showToast('Cache cleared successfully', 'success');
        
        // Reset button
        setTimeout(() => {
          this.innerHTML = originalHTML;
          this.disabled = false;
        }, 1000);
      } catch (error) {
        showToast('Failed to clear cache', 'error');
        this.innerHTML = originalHTML;
        this.disabled = false;
      }
    }
  });
}

// Enhanced scan button with better feedback
const scanBtn = document.getElementById('scanBtn');
const scanLoader = document.getElementById('scanLoader');
const btnText = scanBtn?.querySelector('.btn-text');

if (scanBtn) {
  const originalScanHandler = scanBtn.onclick;
  scanBtn.onclick = async function(e) {
    e.preventDefault();
    
    // Add visual feedback
    this.classList.add('loading');
    btnText.style.opacity = '0.5';
    scanLoader.style.display = 'inline-block';
    
    try {
      if (originalScanHandler) {
        await originalScanHandler.call(this, e);
      }
    } finally {
      // Reset button state
      setTimeout(() => {
        this.classList.remove('loading');
        btnText.style.opacity = '1';
        scanLoader.style.display = 'none';
      }, 500);
    }
  };
}

// Enhanced page scan with progress indicator
const scanPageBtn = document.getElementById('scanPageBtn');
if (scanPageBtn) {
  const originalPageScanHandler = scanPageBtn.onclick;
  scanPageBtn.onclick = async function(e) {
    e.preventDefault();
    
    const pageLoaderEl = document.getElementById('pageLoader');
    const pageButtonText = this.querySelector('.btn-text');
    
    if (pageButtonText) {
      pageButtonText.textContent = 'Scanning...';
    }
    
    if (pageLoaderEl) {
      pageLoaderEl.style.display = 'inline-block';
    }
    
    this.disabled = true;
    
    try {
      if (originalPageScanHandler) {
        await originalPageScanHandler.call(this, e);
      }
      showToast('Page scan completed', 'success');
    } catch (error) {
      showToast('Page scan failed', 'error');
    } finally {
      setTimeout(() => {
        if (pageButtonText) {
          pageButtonText.textContent = 'Scan All Links';
        }
        if (pageLoaderEl) {
          pageLoaderEl.style.display = 'none';
        }
        this.disabled = false;
      }, 500);
    }
  };
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // Ctrl/Cmd + K to focus URL input
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const urlInput = document.getElementById('urlInput');
    if (urlInput) {
      urlInput.focus();
      urlInput.select();
    }
  }
  
  // Escape to clear results
  if (e.key === 'Escape') {
    const scanResult = document.getElementById('scanResult');
    if (scanResult && scanResult.style.display !== 'none') {
      scanResult.style.display = 'none';
      document.getElementById('urlInput').value = '';
    }
  }
  
  // Enter to scan
  if (e.key === 'Enter' && document.activeElement.id === 'urlInput') {
    e.preventDefault();
    scanBtn?.click();
  }
});

// Copy to clipboard functionality
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard', 'success', 2000);
  }).catch(() => {
    showToast('Failed to copy', 'error');
  });
}

// Make domain copyable
const resultDomain = document.getElementById('resultDomain');
if (resultDomain) {
  resultDomain.style.cursor = 'pointer';
  resultDomain.title = 'Click to copy domain';
  resultDomain.addEventListener('click', function() {
    copyToClipboard(this.textContent);
  });
}

// Enhanced help link
const helpLink = document.getElementById('helpLink');
if (helpLink) {
  helpLink.addEventListener('click', function(e) {
    e.preventDefault();
    chrome.tabs.create({ 
      url: 'https://github.com/yourusername/trustlink/wiki' 
    });
  });
}

// Enhanced report issue link
const reportIssueLink = document.getElementById('reportIssueLink');
if (reportIssueLink) {
  reportIssueLink.addEventListener('click', function(e) {
    e.preventDefault();
    chrome.tabs.create({ 
      url: 'https://github.com/yourusername/trustlink/issues/new' 
    });
  });
}

// Auto-update stats every 30 seconds
setInterval(async function() {
  try {
    const stats = await chrome.storage.local.get(['stats']);
    if (stats.stats) {
      document.getElementById('linksScanned').textContent = stats.stats.scanned || 0;
      document.getElementById('threatsBlocked').textContent = stats.stats.blocked || 0;
      document.getElementById('cacheSize').textContent = stats.stats.cached || 0;
    }
  } catch (error) {
    console.error('Failed to update stats:', error);
  }
}, 30000);

// Animate stat cards on load
window.addEventListener('load', function() {
  const statCards = document.querySelectorAll('.stat-card');
  statCards.forEach((card, index) => {
    setTimeout(() => {
      card.style.animation = `slideInRight 0.5s ease-out ${index * 0.1}s both`;
    }, 100);
  });
});

// Enhanced risk score visualization
function updateRiskScore(score, element) {
  const riskProgress = element.querySelector('.risk-progress');
  if (riskProgress) {
    riskProgress.style.width = score + '%';
    
    // Color based on risk level
    if (score < 30) {
      riskProgress.style.background = 'linear-gradient(90deg, #4CAF50, #66BB6A)';
    } else if (score < 70) {
      riskProgress.style.background = 'linear-gradient(90deg, #FF9800, #FFA726)';
    } else {
      riskProgress.style.background = 'linear-gradient(90deg, #F44336, #EF5350)';
    }
    
    // Animate the progress bar
    riskProgress.style.transition = 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
  }
}

// Add pulse animation to status indicator when threats are found
function pulseStatusIndicator(hasThreats) {
  const statusIndicator = document.getElementById('statusIndicator');
  if (statusIndicator) {
    if (hasThreats) {
      statusIndicator.style.animation = 'heartbeat 1s ease-in-out infinite';
    } else {
      statusIndicator.style.animation = 'heartbeat 2s ease-in-out infinite';
    }
  }
}

// Enhanced URL input with real-time validation
const urlInput = document.getElementById('urlInput');
if (urlInput) {
  urlInput.addEventListener('input', function() {
    const value = this.value.trim();
    
    if (value.length === 0) {
      this.style.borderColor = '';
      return;
    }
    
    // Simple URL validation
    const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    
    if (urlPattern.test(value) || value.startsWith('http://') || value.startsWith('https://')) {
      this.style.borderColor = 'rgba(76, 175, 80, 0.5)';
    } else {
      this.style.borderColor = 'rgba(244, 67, 54, 0.5)';
    }
  });
  
  // Add placeholder animation
  const placeholders = [
    'Enter URL to scan...',
    'e.g., https://example.com',
    'Paste suspicious link here...',
    'Check any website for safety...'
  ];
  
  let placeholderIndex = 0;
  setInterval(() => {
    if (document.activeElement !== urlInput) {
      placeholderIndex = (placeholderIndex + 1) % placeholders.length;
      urlInput.placeholder = placeholders[placeholderIndex];
    }
  }, 3000);
}

// Context menu for right-click actions
document.addEventListener('contextmenu', function(e) {
  if (e.target.tagName === 'A' || e.target.closest('a')) {
    // Allow default context menu for links
    return;
  }
  
  if (e.target.id === 'resultDomain' || e.target.classList.contains('result-value')) {
    e.preventDefault();
    copyToClipboard(e.target.textContent);
  }
});

// Add fade-out animation
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOut {
    from {
      opacity: 1;
      transform: translateX(0);
    }
    to {
      opacity: 0;
      transform: translateX(20px);
    }
  }
`;
document.head.appendChild(style);

// Log initialization
console.log('[TrustLink] Enhanced UX features loaded');

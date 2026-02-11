/**
 * TrustLink Browser Extension - Content Script
 * Scans links in real-time on web pages
 */

console.log('[TrustLink] Content script loaded');

// Configuration (loaded from background)
let config = null;
let scanning = false;
let scannedLinks = new Set();
let scanResults = new Map(); // Use Map for better performance
let observer = null;
let scanTimeout = null; // For debouncing

// Initialize
(async function init() {
  try {
    // Get configuration from background
    const response = await chrome.runtime.sendMessage({ action: 'getConfig' });
    config = response;
    
    if (config.enableRealTimeScanning) {
      console.log('[TrustLink] Real-time scanning enabled');
      
      // Scan existing links
      if (config.autoScanOnPageLoad) {
        setTimeout(() => scanPageLinks(), config.scanDelay);
      }
      
      // Watch for new links
      startLinkObserver();
    }
  } catch (error) {
    console.error('[TrustLink] Initialization error:', error);
  }
})();

/**
 * Scan all links on the page
 */
async function scanPageLinks() {
  if (scanning) return;
  scanning = true;
  
  try {
    // Get all anchor tags (performance optimized)
    const links = document.querySelectorAll('a[href]');
    const urlsToScan = [];
    const linkElements = [];
    const linkMap = new Map(); // Track link-to-element mapping
    
    // Batch process links for better performance
    const currentDomain = window.location.hostname;
    
    for (const link of links) {
      const href = link.href;
      
      // Skip already scanned links
      if (scannedLinks.has(href)) continue;
      
      // Skip internal anchors and javascript links
      if (href.startsWith('#') || href.startsWith('javascript:')) continue;
      
      // Skip navigation, header, and menu links (performance optimized check)
      if (link.closest('nav, header, [role="navigation"], .nav, .navbar, .menu, .header')) continue;
      
      // Add to scan queue
      if (!linkMap.has(href)) {
        urlsToScan.push(href);
        linkMap.set(href, []);
      }
      linkMap.get(href).push(link);
      linkElements.push(link);
      scannedLinks.add(href);
    }
    
    if (urlsToScan.length === 0) {
      scanning = false;
      return;
    }
    
    console.log(`[TrustLink] Scanning ${urlsToScan.length} links...`);
    
    // Show loading state on all links being scanned
    for (const link of linkElements) {
      link.classList.add('trustlink-analyzing');
      link.setAttribute('data-trustlink-tooltip', 'Analyzing link security...');
    }
    
    // Batch scan URLs (backend handles timing delay)
    const results = await chrome.runtime.sendMessage({
      action: 'batchScan',
      urls: urlsToScan
    });
    
    // Process results and collect for display (optimized)
    let phishingCount = 0;
    let warningCount = 0;
    let safeCount = 0;
    const threatsFound = [];
    
    // Batch DOM updates for better performance
    const updates = [];
    
    for (const url of urlsToScan) {
      const result = results[url];
      const links = linkMap.get(url);
      
      if (result && result.status === 'success') {
        scanResults.set(url, result);
        
        const isPhishing = result.prediction === 'Phishing' && result.confidence >= config.confidenceThreshold;
        
        // Apply to all elements with this URL
        for (const link of links) {
          link.classList.remove('trustlink-analyzing');
          updates.push({ link, result });
        }
        
        if (isPhishing) {
          phishingCount++;
          
          // Collect threat information for popup (only once per URL)
          threatsFound.push({
            url: url,
            domain: new URL(url).hostname,
            confidence: result.confidence,
            riskLevel: result.risk_level || 'medium',
            element: links[0],
            result: result  // Store full result data for detailed display
          });
        } else {
          safeCount++;
        }
      } else {
        // Remove analyzing state even if scan failed
        for (const link of links) {
          link.classList.remove('trustlink-analyzing');
        }
      }
    }
    
    // Apply all link indicators in batch (reduces reflows)
    requestAnimationFrame(() => {
      for (const { link, result } of updates) {
        applyLinkIndicator(link, result);
      }
    });
    
    // Show results popup with scan summary
    showScanResultsPopup({
      total: urlsToScan.length,
      safe: safeCount,
      threats: phishingCount,
      warnings: warningCount,
      threatsFound: threatsFound
    });
    
    // Update badge
    chrome.runtime.sendMessage({
      action: 'updateBadge',
      count: phishingCount
    });
    
  } catch (error) {
    console.error('[TrustLink] Scan error:', error);
  } finally {
    scanning = false;
  }
}

/**
 * Apply visual indicator to a link based on scan result
 */
function applyLinkIndicator(link, result) {
  // Remove existing indicators (including analyzing state)
  link.classList.remove('trustlink-safe', 'trustlink-warning', 'trustlink-danger', 'trustlink-analyzing', 'trustlink-blocked');
  
  const isPhishing = result.prediction === 'Phishing';
  const confidence = result.confidence;
  const riskLevel = result.risk_level;
  
  // Determine indicator class
  let indicatorClass = '';
  let indicatorText = '';
  let indicatorColor = '';
  let shouldBlock = false;
  
  if (isPhishing && confidence >= config.confidenceThreshold) {
    // Phishing detected with high confidence
    if (riskLevel === 'high') {
      indicatorClass = 'trustlink-danger';
      indicatorText = `DANGER: Phishing Detected (${confidence}% confidence)`;
      indicatorColor = '#dc3545';
      
      // Safe mode: block high-risk links
      if (config.safeMode && config.safeModeStrength !== 'low') {
        shouldBlock = true;
      }
    } else if (riskLevel === 'medium') {
      indicatorClass = 'trustlink-warning';
      indicatorText = `Warning: Potential Phishing (${confidence}% confidence)`;
      indicatorColor = '#ffc107';
      
      // Safe mode high: also block medium-risk links
      if (config.safeMode && config.safeModeStrength === 'high') {
        shouldBlock = true;
      }
    } else {
      indicatorClass = 'trustlink-warning';
      indicatorText = `Suspicious Link (${confidence}% confidence)`;
      indicatorColor = '#ffc107';
    }
    
  } else if (!isPhishing && config.showSafeIndicators && confidence >= 70) {
    // Safe link with high confidence
    indicatorClass = 'trustlink-safe';
    indicatorText = `Safe Link (${confidence}% confidence)`;
    indicatorColor = '#28a745';
  }
  
  // Apply class
  if (indicatorClass) {
    link.classList.add(indicatorClass);
  }
  
  // Safe mode: Block dangerous links
  if (shouldBlock) {
    link.classList.add('trustlink-blocked');
    link.setAttribute('data-trustlink-blocked', 'true');
    link.setAttribute('data-original-href', link.href);
    link.href = 'javascript:void(0)';
    indicatorText += ' [BLOCKED BY SAFE MODE]';
    
    // Add blocked indicator
    const blockedBadge = document.createElement('span');
    blockedBadge.className = 'trustlink-blocked-badge';
    blockedBadge.innerHTML = '<i class="fas fa-ban"></i> BLOCKED';
    blockedBadge.style.cssText = `
      display: inline-block;
      background: #dc3545;
      color: white;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 10px;
      font-weight: bold;
      margin-left: 5px;
      vertical-align: middle;
    `;
    
    // Insert badge after link text
    if (!link.querySelector('.trustlink-blocked-badge')) {
      link.appendChild(blockedBadge);
    }
  }
  
  // Add tooltip
  if (indicatorText) {
    link.setAttribute('data-trustlink-tooltip', indicatorText);
    link.setAttribute('title', indicatorText);
  }
  
  // Add click warning for dangerous links (if not blocked)
  if (isPhishing && confidence >= config.confidenceThreshold && riskLevel === 'high' && !shouldBlock) {
    link.addEventListener('click', handleDangerousLinkClick, { capture: true });
  } else if (shouldBlock) {
    link.addEventListener('click', handleBlockedLinkClick, { capture: true });
  }
}

/**
 * Handle click on dangerous link
 */
function handleDangerousLinkClick(event) {
  event.preventDefault();
  event.stopPropagation();
  
  const link = event.currentTarget;
  const url = link.href;
  const result = scanResults.get(url);
  
  if (!result) return;
  
  // Show warning modal
  const proceed = confirm(
    `PHISHING WARNING\n\n` +
    `This link has been identified as a potential phishing attempt:\n\n` +
    `URL: ${url}\n` +
    `Confidence: ${result.confidence}%\n` +
    `Risk Level: ${result.risk_level.toUpperCase()}\n\n` +
    `Risk Factors:\n${(result.risk_assessment?.risk_factors || []).map(f => `• ${f}`).join('\n')}\n\n` +
    `Are you sure you want to proceed?\n\n` +
    `Click OK to continue at your own risk, or Cancel to stay safe.`
  );
  
  if (proceed) {
    // User chose to proceed - open in new tab with warning
    window.open(url, '_blank');
  }
  
  return false;
}

/**
 * Handle click on blocked link (Safe Mode)
 */
function handleBlockedLinkClick(event) {
  event.preventDefault();
  event.stopPropagation();
  
  const link = event.currentTarget;
  const originalUrl = link.getAttribute('data-original-href');
  const result = scanResults.get(originalUrl);
  
  if (!result) return;
  
  // Show blocked message with option to override
  const override = confirm(
    `🛡️ SAFE MODE - LINK BLOCKED\n\n` +
    `This dangerous link has been blocked by TrustLink Safe Mode:\n\n` +
    `URL: ${originalUrl}\n` +
    `Threat Level: ${result.risk_level.toUpperCase()}\n` +
    `Confidence: ${result.confidence}%\n\n` +
    `${(result.risk_assessment?.risk_factors || []).map(f => `• ${f}`).join('\n')}\n\n` +
    `⚠️ WARNING: Visiting this link may compromise your security!\n\n` +
    `Do you want to override Safe Mode and visit this link anyway?\n` +
    `(This is NOT recommended)`
  );
  
  if (override) {
    // User chose to override - show final confirmation
    const finalConfirm = confirm(
      `⚠️ FINAL WARNING ⚠️\n\n` +
      `You are about to visit a potentially dangerous website.\n\n` +
      `This could result in:\n` +
      `• Stolen passwords and personal information\n` +
      `• Financial fraud\n` +
      `• Malware installation\n` +
      `• Identity theft\n\n` +
      `Are you absolutely sure you want to continue?`
    );
    
    if (finalConfirm) {
      // Open with extreme warning
      window.open(originalUrl, '_blank');
      
      // Log override for security tracking
      chrome.runtime.sendMessage({
        action: 'logSafeModeOverride',
        url: originalUrl,
        riskLevel: result.risk_level
      });
    }
  }
  
  return false;
}

/**
 * Start observing DOM for new links (optimized with debouncing)
 */
function startLinkObserver() {
  if (observer) return;
  
  observer = new MutationObserver((mutations) => {
    let hasNewLinks = false;
    
    // Optimized mutation checking
    for (const mutation of mutations) {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.tagName === 'A' && node.href) {
              hasNewLinks = true;
              break;
            } else if (node.querySelectorAll && node.querySelectorAll('a[href]').length > 0) {
              hasNewLinks = true;
              break;
            }
          }
        }
        if (hasNewLinks) break;
      }
    }
    
    if (hasNewLinks) {
      // Debounce scanning for better performance
      if (scanTimeout) clearTimeout(scanTimeout);
      scanTimeout = setTimeout(() => {
        scanPageLinks();
      }, config.scanDelay);
    }
  });
  
  // Observe with throttling for better performance
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  console.log('[TrustLink] Link observer started');
}

/**
 * Stop observing DOM
 */
function stopLinkObserver() {
  if (observer) {
    observer.disconnect();
    observer = null;
    console.log('[TrustLink] Link observer stopped');
  }
}

// Listen for configuration changes
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'configUpdated') {
    const oldConfig = config;
    config = request.config;
    
    // If safe mode settings changed, rescan page
    if (oldConfig && (oldConfig.safeMode !== config.safeMode || oldConfig.safeModeStrength !== config.safeModeStrength)) {
      console.log('[TrustLink] Safe mode settings changed, rescanning page...');
      
      // Clear existing scan data
      scannedLinks.clear();
      scanResults.clear();
      
      // Remove all existing indicators
      document.querySelectorAll('a[class*="trustlink-"]').forEach(link => {
        link.classList.remove('trustlink-safe', 'trustlink-warning', 'trustlink-danger', 'trustlink-blocked', 'trustlink-analyzing');
        link.removeAttribute('data-trustlink-tooltip');
        link.removeAttribute('data-trustlink-blocked');
        link.removeAttribute('data-original-href');
        const badge = link.querySelector('.trustlink-blocked-badge');
        if (badge) badge.remove();
      });
      
      // Rescan page with new settings
      setTimeout(() => scanPageLinks(), 500);
    }
    
    if (config.enableRealTimeScanning && !observer) {
      startLinkObserver();
      scanPageLinks();
    } else if (!config.enableRealTimeScanning && observer) {
      stopLinkObserver();
    }
  }
});

// Manual scan trigger
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scanPage') {
    scannedLinks.clear();
    scanResults = {};
    scanPageLinks().then(() => {
      sendResponse({ success: true });
    });
    return true;
  }
});

/**
 * Show scan results popup
 */
function showScanResultsPopup(results) {
  // Remove existing popup if any
  const existingPopup = document.getElementById('trustlink-scan-results-popup');
  if (existingPopup) {
    existingPopup.remove();
  }
  
  // Create popup container
  const popup = document.createElement('div');
  popup.id = 'trustlink-scan-results-popup';
  popup.className = 'trustlink-results-popup';
  
  // Create popup content
  const hasThreats = results.threats > 0;
  const popupHTML = `
    <div class="trustlink-popup-header ${hasThreats ? 'has-threats' : 'all-safe'}">
      <div class="trustlink-popup-title">
        <i class="fas ${hasThreats ? 'fa-shield-alt' : 'fa-check-circle'}"></i>
        <span>TrustLink Scan Complete</span>
      </div>
      <button class="trustlink-popup-close" id="trustlink-close-popup">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div class="trustlink-popup-body">
      <div class="trustlink-scan-summary">
        <div class="trustlink-summary-stat">
          <div class="stat-icon">
            <i class="fas fa-link"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">${results.total}</div>
            <div class="stat-label">Links Scanned</div>
          </div>
        </div>
        
        <div class="trustlink-summary-stat safe">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">${results.safe}</div>
            <div class="stat-label">Safe</div>
          </div>
        </div>
        
        <div class="trustlink-summary-stat ${hasThreats ? 'danger' : ''}">
          <div class="stat-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">${results.threats}</div>
            <div class="stat-label">Threats</div>
          </div>
        </div>
      </div>
      
      ${hasThreats ? `
        <div class="trustlink-threats-section">
          <div class="threats-header">
            <i class="fas fa-exclamation-circle"></i>
            <strong>Threats Detected:</strong>
          </div>
          <div class="threats-list">
            ${results.threatsFound.map((threat, index) => {
              const result = threat.result || {};
              const urlStructure = result.url_structure || {};
              const securityInfo = result.security_info || {};
              const domainInfo = result.domain_info || {};
              const externalVerification = result.external_verification || result.external_verifier || {};
              const features = result.features || {};
              
              return `
              <div class="threat-item-enhanced ${threat.riskLevel}">
                <div class="threat-header-enhanced">
                  <div class="threat-number-enhanced">${index + 1}</div>
                  <div class="threat-info-main">
                    <div class="threat-domain-enhanced">${threat.domain}</div>
                    <div class="threat-badges">
                      <span class="threat-risk ${threat.riskLevel}">
                        ${threat.riskLevel.toUpperCase()} RISK
                      </span>
                      <span class="threat-confidence-badge">${threat.confidence}% confidence</span>
                      ${result.threat_category ? `<span class="threat-category-small">${result.threat_category.replace(/_/g, ' ').toUpperCase()}</span>` : ''}
                    </div>
                  </div>
                  <button class="threat-toggle" data-threat-index="${index}" title="Show/Hide Details">
                    <i class="fas fa-chevron-down"></i>
                  </button>
                </div>
                
                <div class="threat-details-panel" id="threat-details-${index}" style="display: none;">
                  <!-- Security Analysis -->
                  <div class="threat-section">
                    <div class="threat-section-title">
                      <i class="fas fa-lock"></i> Security Analysis
                    </div>
                    <div class="threat-section-grid">
                      <div class="threat-detail-item">
                        <span class="detail-icon ${urlStructure.is_https ? 'success' : 'danger'}">
                          <i class="fas fa-shield-alt"></i>
                        </span>
                        <div class="detail-content">
                          <div class="detail-label">HTTPS</div>
                          <div class="detail-value ${urlStructure.is_https ? 'success' : 'danger'}">
                            ${urlStructure.is_https ? 'Enabled' : 'Not Enabled'}
                          </div>
                        </div>
                      </div>
                      <div class="threat-detail-item">
                        <span class="detail-icon ${securityInfo.has_valid_ssl ? 'success' : 'danger'}">
                          <i class="fas fa-certificate"></i>
                        </span>
                        <div class="detail-content">
                          <div class="detail-label">SSL Certificate</div>
                          <div class="detail-value ${securityInfo.has_valid_ssl ? 'success' : 'danger'}">
                            ${securityInfo.has_valid_ssl ? 'Valid' : 'Invalid/Missing'}
                          </div>
                        </div>
                      </div>
                      <div class="threat-detail-item">
                        <span class="detail-icon ${domainInfo.domain_age_days > 730 ? 'success' : domainInfo.domain_age_days > 180 ? 'warning' : 'danger'}">
                          <i class="fas fa-calendar-alt"></i>
                        </span>
                        <div class="detail-content">
                          <div class="detail-label">Domain Age</div>
                          <div class="detail-value">
                            ${urlStructure.domain_age_readable || 'Unknown'}
                          </div>
                        </div>
                      </div>
                      <div class="threat-detail-item">
                        <span class="detail-icon ${domainInfo.has_dns_record ? 'success' : 'danger'}">
                          <i class="fas fa-server"></i>
                        </span>
                        <div class="detail-content">
                          <div class="detail-label">DNS Records</div>
                          <div class="detail-value">
                            ${domainInfo.has_dns_record && domainInfo.has_mx_record ? 'Complete' : domainInfo.has_dns_record ? 'Partial' : 'Missing'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- URL Structure -->
                  <div class="threat-section">
                    <div class="threat-section-title">
                      <i class="fas fa-link"></i> URL Analysis
                    </div>
                    <div class="threat-section-list">
                      <div class="threat-list-item">
                        <span class="list-label">Protocol:</span>
                        <span class="list-value">${(urlStructure.protocol || 'http').toUpperCase()}</span>
                      </div>
                      <div class="threat-list-item">
                        <span class="list-label">Subdomains:</span>
                        <span class="list-value ${features.num_subdomains > 2 ? 'warning' : ''}">${features.num_subdomains || 0}</span>
                      </div>
                      <div class="threat-list-item">
                        <span class="list-label">URL Length:</span>
                        <span class="list-value ${urlStructure.url_length > 100 ? 'warning' : ''}">${urlStructure.url_length || 0} chars</span>
                      </div>
                      <div class="threat-list-item">
                        <span class="list-label">Entropy:</span>
                        <span class="list-value">${features.url_entropy ? features.url_entropy.toFixed(2) : '0.00'}</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- External Verification -->
                  ${externalVerification.verifiers_consulted && externalVerification.verifiers_consulted.length > 0 ? `
                  <div class="threat-section">
                    <div class="threat-section-title">
                      <i class="fas fa-shield-virus"></i> External Verification
                    </div>
                    <div class="threat-section-list">
                      ${externalVerification.verifiers_consulted.includes('virustotal') || externalVerification.verifiers_consulted.includes('VirusTotal') ? `
                      <div class="threat-list-item">
                        <span class="list-icon ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'danger' : 'success'}">
                          <i class="fas fa-shield-virus"></i>
                        </span>
                        <span class="list-text ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'danger' : 'success'}">
                          VirusTotal: ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'Flagged' : 'Clean'}
                        </span>
                      </div>
                      ` : ''}
                      ${externalVerification.verifiers_consulted.includes('google') || externalVerification.verifiers_consulted.includes('Google Safe Browsing') ? `
                      <div class="threat-list-item">
                        <span class="list-icon ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'danger' : 'success'}">
                          <i class="fab fa-google"></i>
                        </span>
                        <span class="list-text ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'danger' : 'success'}">
                          Google Safe Browsing: ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'Flagged' : 'Clean'}
                        </span>
                      </div>
                      ` : ''}
                      ${externalVerification.verifiers_consulted.includes('phishtank') || externalVerification.verifiers_consulted.includes('PhishTank') ? `
                      <div class="threat-list-item">
                        <span class="list-icon ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'danger' : 'success'}">
                          <i class="fas fa-database"></i>
                        </span>
                        <span class="list-text ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'danger' : 'success'}">
                          PhishTank: ${externalVerification.threat_intelligence_match && externalVerification.external_consensus === 'threat' ? 'Found in Database' : 'Not in Database'}
                        </span>
                      </div>
                      ` : ''}
                    </div>
                  </div>
                  ` : ''}
                  
                  <!-- Actions -->
                  <div class="threat-actions">
                    <button class="threat-action-btn highlight-btn" data-highlight-index="${index}">
                      <i class="fas fa-crosshairs"></i> Highlight Link
                    </button>
                    <button class="threat-action-btn copy-btn" data-copy-url="${threat.url || ''}">
                      <i class="fas fa-copy"></i> Copy URL
                    </button>
                  </div>
                </div>
              </div>
            `;
            }).join('')}
          </div>
        </div>
      ` : `
        <div class="trustlink-safe-message">
          <i class="fas fa-shield-check"></i>
          <p><strong>All links appear safe!</strong></p>
          <p>No phishing threats detected on this page.</p>
        </div>
      `}
    </div>
    
    <div class="trustlink-popup-footer">
      <button class="trustlink-btn trustlink-btn-secondary" id="trustlink-dismiss-popup">
        Dismiss
      </button>
      ${hasThreats ? `
        <button class="trustlink-btn trustlink-btn-primary" id="trustlink-view-details">
          <i class="fas fa-info-circle"></i>
          View Details
        </button>
      ` : ''}
    </div>
  `;
  
  popup.innerHTML = popupHTML;
  document.body.appendChild(popup);
  
  // Add event listeners
  const closeBtn = document.getElementById('trustlink-close-popup');
  const dismissBtn = document.getElementById('trustlink-dismiss-popup');
  const viewDetailsBtn = document.getElementById('trustlink-view-details');
  
  if (closeBtn) {
    closeBtn.addEventListener('click', () => popup.remove());
  }
  
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => popup.remove());
  }
  
  if (viewDetailsBtn) {
    viewDetailsBtn.addEventListener('click', () => {
      // Open extension popup with details
      chrome.runtime.sendMessage({ action: 'openPopup' });
      popup.remove();
    });
  }
  
  // Toggle threat details
  const toggleButtons = popup.querySelectorAll('.threat-toggle');
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = e.currentTarget.dataset.threatIndex;
      const detailsPanel = document.getElementById(`threat-details-${index}`);
      const icon = e.currentTarget.querySelector('i');
      
      if (detailsPanel.style.display === 'none') {
        detailsPanel.style.display = 'block';
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');
      } else {
        detailsPanel.style.display = 'none';
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
      }
    });
  });
  
  // Highlight threat buttons
  const highlightButtons = popup.querySelectorAll('.highlight-btn');
  highlightButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const index = parseInt(e.currentTarget.dataset.highlightIndex);
      const threat = results.threatsFound[index];
      if (threat.element) {
        // Scroll to and highlight the dangerous link
        threat.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        threat.element.classList.add('trustlink-highlight-pulse');
        setTimeout(() => {
          threat.element.classList.remove('trustlink-highlight-pulse');
        }, 3000);
      }
    });
  });
  
  // Copy URL buttons
  const copyButtons = popup.querySelectorAll('.copy-btn');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const url = e.currentTarget.dataset.copyUrl;
      try {
        await navigator.clipboard.writeText(url);
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
          btn.innerHTML = '<i class="fas fa-copy"></i> Copy URL';
        }, 2000);
      } catch (err) {
        console.error('Failed to copy URL:', err);
      }
    });
  });
  
  // Auto-dismiss after 10 seconds if all safe
  if (!hasThreats) {
    setTimeout(() => {
      if (popup.parentNode) {
        popup.remove();
      }
    }, 10000);
  }
  
  // Animate in
  setTimeout(() => {
    popup.classList.add('show');
  }, 100);
}

console.log('[TrustLink] Content script initialized');

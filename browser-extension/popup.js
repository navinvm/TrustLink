/**
 * TrustLink Browser Extension - Popup Script
 */

// DOM Elements
const urlInput = document.getElementById('urlInput');
const scanBtn = document.getElementById('scanBtn');
const scanLoader = document.getElementById('scanLoader');
const scanResult = document.getElementById('scanResult');
const resultIcon = document.getElementById('resultIcon');
const resultVerdict = document.getElementById('resultVerdict');
const resultConfidence = document.getElementById('resultConfidence');
const resultRisk = document.getElementById('resultRisk');
const resultDomain = document.getElementById('resultDomain');
const viewDetailsBtn = document.getElementById('viewDetailsBtn');

const currentPageUrl = document.getElementById('currentPageUrl');
const scanPageBtn = document.getElementById('scanPageBtn');
const pageLoader = document.getElementById('pageLoader');
const pageStats = document.getElementById('pageStats');
const totalLinks = document.getElementById('totalLinks');
const threatsFound = document.getElementById('threatsFound');

const linksScanned = document.getElementById('linksScanned');
const threatsBlocked = document.getElementById('threatsBlocked');
const cacheSize = document.getElementById('cacheSize');

const clearCacheBtn = document.getElementById('clearCacheBtn');
const optionsBtn = document.getElementById('optionsBtn');

let currentScanResult = null;
let config = null;

// Initialize popup
(async function init() {
  try {
    // Load configuration
    config = await chrome.runtime.sendMessage({ action: 'getConfig' });
    
    // Load stats
    await loadStats();
    
    // Get current tab info
    await loadCurrentTab();
    
    // Setup event listeners
    setupEventListeners();
    
  } catch (error) {
    console.error('[TrustLink] Popup initialization error:', error);
  }
})();

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Scan URL button
  scanBtn.addEventListener('click', handleQuickScan);
  
  // Enter key in URL input
  urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleQuickScan();
    }
  });
  
  // Scan current page button
  scanPageBtn.addEventListener('click', handlePageScan);
  
  // View details button
  viewDetailsBtn.addEventListener('click', () => {
    if (currentScanResult && currentScanResult.url) {
      // Open full analysis in new tab (dashboard)
      const dashboardUrl = `${config.apiUrl}/dashboard`;
      chrome.tabs.create({ url: dashboardUrl });
    }
  });
  
  // Clear cache button
  clearCacheBtn.addEventListener('click', async () => {
    if (confirm('Clear all cached scan results?')) {
      await chrome.runtime.sendMessage({ action: 'clearCache' });
      await loadStats();
      showNotification('Cache cleared successfully', 'success');
    }
  });
  
  // Options button
  optionsBtn.addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });
  
  // View Dashboard button
  const viewDashboardBtn = document.getElementById('viewDashboardBtn');
  if (viewDashboardBtn) {
    viewDashboardBtn.addEventListener('click', () => {
      const dashboardUrl = config?.apiUrl ? `${config.apiUrl}/dashboard` : 'http://localhost:5000/dashboard';
      chrome.tabs.create({ url: dashboardUrl });
    });
  }
  
  // Safe Mode toggle
  const safeModeToggle = document.getElementById('safeModeToggle');
  const safeModeControls = document.getElementById('safeModeControls');
  const safeModeStrength = document.getElementById('safeModeStrength');
  
  if (safeModeToggle) {
    // Load current safe mode status
    safeModeToggle.checked = config?.safeMode || false;
    safeModeControls.style.display = safeModeToggle.checked ? 'block' : 'none';
    
    if (safeModeStrength && config?.safeModeStrength) {
      safeModeStrength.value = config.safeModeStrength;
    }
    
    // Toggle safe mode
    safeModeToggle.addEventListener('change', async () => {
      const enabled = safeModeToggle.checked;
      safeModeControls.style.display = enabled ? 'block' : 'none';
      
      // Update config
      await chrome.runtime.sendMessage({
        action: 'updateConfig',
        config: { safeMode: enabled }
      });
      
      // Reload config
      config = await chrome.runtime.sendMessage({ action: 'getConfig' });
      
      // Notify content scripts
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.id) {
        chrome.tabs.sendMessage(tab.id, {
          action: 'configUpdated',
          config: config
        });
      }
      
      showNotification(
        enabled ? 'Safe Mode Enabled - Dangerous links will be blocked' : 'Safe Mode Disabled',
        enabled ? 'success' : 'info'
      );
    });
  }
  
  // Safe Mode strength selector
  if (safeModeStrength) {
    safeModeStrength.addEventListener('change', async () => {
      const strength = safeModeStrength.value;
      
      // Update config
      await chrome.runtime.sendMessage({
        action: 'updateConfig',
        config: { safeModeStrength: strength }
      });
      
      // Reload config
      config = await chrome.runtime.sendMessage({ action: 'getConfig' });
      
      // Notify content scripts
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.id) {
        chrome.tabs.sendMessage(tab.id, {
          action: 'configUpdated',
          config: config
        });
      }
      
      const strengthText = strength === 'high' ? 'High' : strength === 'low' ? 'Low' : 'Medium';
      showNotification(`Safe Mode strength set to ${strengthText}`, 'success');
    });
  }
  
  // Scan current page quick button
  const scanCurrentPageQuick = document.getElementById('scanCurrentPageQuick');
  if (scanCurrentPageQuick) {
    scanCurrentPageQuick.addEventListener('click', handleScanCurrentUrl);
  }
  
  // Paste and scan button
  const pasteAndScanBtn = document.getElementById('pasteAndScanBtn');
  if (pasteAndScanBtn) {
    pasteAndScanBtn.addEventListener('click', handlePasteAndScan);
  }
  
  // Scan current URL button
  const scanCurrentUrlBtn = document.getElementById('scanCurrentUrlBtn');
  if (scanCurrentUrlBtn) {
    scanCurrentUrlBtn.addEventListener('click', handleScanCurrentUrl);
  }
  
  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+V - Paste and scan
    if (e.ctrlKey && e.shiftKey && e.key === 'V') {
      e.preventDefault();
      handlePasteAndScan();
    }
    // Ctrl+Enter - Scan current page
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      handleScanCurrentUrl();
    }
  });
  
  // Flagged dropdown toggle
  const flaggedToggle = document.getElementById('flaggedToggle');
  if (flaggedToggle) {
    flaggedToggle.addEventListener('click', () => {
      const flaggedContent = document.getElementById('flaggedContent');
      const arrow = flaggedToggle.querySelector('.dropdown-arrow');
      flaggedToggle.classList.toggle('active');
      if (flaggedContent) {
        const isVisible = flaggedContent.style.display !== 'none';
        flaggedContent.style.display = isVisible ? 'none' : 'block';
        if (arrow) {
          arrow.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
        }
      }
    });
  }
}

/**
 * Load statistics
 */
async function loadStats() {
  try {
    // Get cache stats
    const cacheStats = await chrome.runtime.sendMessage({ action: 'getCacheStats' });
    
    if (cacheStats) {
      cacheSize.textContent = cacheStats.valid || 0;
      linksScanned.textContent = cacheStats.total || 0;
    }
    
    // Retrieve threat count from storage
    chrome.storage.local.get(['threatCount'], function(result) {
        if (result.threatCount) {
            document.getElementById('threatCount').textContent = result.threatCount;
        }
    });
    threatsBlocked.textContent = '0';
    
  } catch (error) {
    console.error('[TrustLink] Error loading stats:', error);
  }
}

/**
 * Load current tab information
 */
async function loadCurrentTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab && tab.url) {
      const url = new URL(tab.url);
      currentPageUrl.textContent = url.hostname + url.pathname;
      currentPageUrl.title = tab.url;
    } else {
      currentPageUrl.textContent = 'No active page';
      scanPageBtn.disabled = true;
    }
  } catch (error) {
    console.error('[TrustLink] Error loading current tab:', error);
    currentPageUrl.textContent = 'Error loading page';
    scanPageBtn.disabled = true;
  }
}

/**
 * Handle quick URL scan
 */
async function handleQuickScan() {
  const url = urlInput.value.trim();
  
  if (!url) {
    showNotification('Please enter a URL', 'error');
    return;
  }
  
  // Validate URL format
  if (!isValidUrl(url)) {
    showNotification('Please enter a valid URL', 'error');
    return;
  }
  
  // Show loading state
  scanBtn.disabled = true;
  scanBtn.querySelector('.btn-text').style.display = 'none';
  scanLoader.style.display = 'inline-block';
  scanResult.style.display = 'none';
  
  try {
    // Scan URL
    const result = await chrome.runtime.sendMessage({
      action: 'scanUrl',
      url: url
    });
    
    if (result.status === 'success') {
      currentScanResult = result;
      displayScanResult(result);
      scanResult.style.display = 'block';
    } else {
      showNotification(`Scan failed: ${result.error || 'Unknown error'}`, 'error');
    }
    
  } catch (error) {
    console.error('[TrustLink] Scan error:', error);
    showNotification('Scan failed. Please check your connection.', 'error');
  } finally {
    // Reset loading state
    scanBtn.disabled = false;
    scanBtn.querySelector('.btn-text').style.display = 'inline';
    scanLoader.style.display = 'none';
  }
}

/**
 * Display scan result
 */
function displayScanResult(result) {
  const isPhishing = result.prediction === 'Phishing';
  const confidence = result.confidence;
  const riskLevel = result.risk_level || 'low';
  const features = result.features || {};
  const urlStructure = result.url_structure || {};
  
  // Get elements
  const statusShield = document.getElementById('statusShield');
  const shieldIcon = document.getElementById('shieldIcon');
  const shieldVerdict = document.getElementById('shieldVerdict');
  const shieldSubtitle = document.getElementById('shieldSubtitle');
  
  // Set status shield
  statusShield.className = 'status-shield';
  if (isPhishing) {
    if (riskLevel === 'high') {
      statusShield.classList.add('danger');
      shieldVerdict.textContent = 'DANGER - Phishing Detected';
      shieldSubtitle.textContent = 'High-risk malicious website';
    } else if (riskLevel === 'medium') {
      statusShield.classList.add('warning');
      shieldVerdict.textContent = 'WARNING - Suspicious Link';
      shieldSubtitle.textContent = 'Medium-risk potentially harmful';
    } else {
      statusShield.classList.add('warning');
      shieldVerdict.textContent = 'CAUTION - Potentially Unsafe';
      shieldSubtitle.textContent = 'Low-risk but questionable';
    }
  } else {
    statusShield.classList.add('safe');
    shieldVerdict.textContent = 'SAFE - Legitimate Website';
    shieldSubtitle.textContent = 'No threats detected';
  }
  
  // Update pattern metrics
  const entropy = features.url_entropy || 0;
  const urlLength = urlStructure.length || 0;
  const specialChars = features.special_char_count || 0;
  
  document.getElementById('entropyValue').textContent = entropy.toFixed(2);
  document.getElementById('lengthValue').textContent = urlLength;
  document.getElementById('specialCharsValue').textContent = specialChars;
  
  // Update progress bars
  document.getElementById('entropyProgress').style.width = `${Math.min(entropy * 20, 100)}%`;
  document.getElementById('lengthProgress').style.width = `${Math.min((urlLength / 100) * 100, 100)}%`;
  document.getElementById('specialCharsProgress').style.width = `${Math.min((specialChars / 20) * 100, 100)}%`;
  
  // Update confidence score
  document.getElementById('confidenceValue').textContent = `${confidence}%`;
  const confidenceProgress = document.getElementById('confidenceProgress');
  confidenceProgress.style.width = `${confidence}%`;
  
  // Color confidence bar based on result
  if (isPhishing) {
    if (riskLevel === 'high') {
      confidenceProgress.style.background = 'linear-gradient(90deg, #dc3545, #c82333)';
    } else {
      confidenceProgress.style.background = 'linear-gradient(90deg, #ffc107, #ff9500)';
    }
  } else {
    confidenceProgress.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
  }
  
  // Show zero-day alert if applicable (ML detected but external sources didn't)
  const zeroDayAlert = document.getElementById('zeroDayAlert');
  const verification = result.external_verification || result.external_verifier || {};
  const isZeroDay = isPhishing && 
                    verification.verifiers_consulted && 
                    verification.verifiers_consulted.length > 0 && 
                    (!verification.threat_intelligence_match || verification.external_consensus === 'safe');
  
  if (isZeroDay) {
    zeroDayAlert.classList.remove('hidden');
  } else {
    zeroDayAlert.classList.add('hidden');
  }
  
  // Update status badges
  const statusBadge = document.getElementById('statusBadge');
  const riskLevelBadge = document.getElementById('riskLevel');
  
  if (isPhishing) {
    statusBadge.textContent = 'Phishing';
    statusBadge.className = 'status-badge-glass danger';
  } else {
    statusBadge.textContent = 'Safe';
    statusBadge.className = 'status-badge-glass safe';
  }
  
  riskLevelBadge.textContent = riskLevel.toUpperCase();
  riskLevelBadge.className = `risk-badge-glass ${riskLevel}`;
  
  // Update threat category
  const threatCategory = document.getElementById('threatCategory');
  if (threatCategory && result.threat_category) {
    threatCategory.textContent = result.threat_category.replace(/_/g, ' ').toUpperCase();
    threatCategory.className = 'threat-category-badge';
  }
  
  // Populate details list
  const detailsList = document.getElementById('detailsList');
  detailsList.innerHTML = '';
  
  const details = [];
  
  // Add key details
  details.push(`<i class="fas fa-globe"></i> Domain: ${urlStructure.domain || 'Unknown'}`);
  details.push(`<i class="fas fa-link"></i> URL Length: ${urlLength} characters`);
  details.push(`<i class="fas fa-fingerprint"></i> Entropy: ${entropy.toFixed(2)}`);
  
  if (features.has_ip_address) {
    details.push(`<i class="fas fa-exclamation-circle"></i> Uses IP address instead of domain`);
  }
  
  if (features.subdomain_count > 2) {
    details.push(`<i class="fas fa-sitemap"></i> Multiple subdomains detected (${features.subdomain_count})`);
  }
  
  if (features.suspicious_keywords > 0) {
    details.push(`<i class="fas fa-search"></i> Contains ${features.suspicious_keywords} suspicious keyword(s)`);
  }
  
  if (features.has_at_symbol) {
    details.push(`<i class="fas fa-at"></i> Contains @ symbol (URL obfuscation)`);
  }
  
  if (features.dots_in_domain > 3) {
    details.push(`<i class="fas fa-ellipsis-h"></i> Excessive dots in domain (${features.dots_in_domain})`);
  }
  
  // Check both external_verification and external_verifier for backward compatibility
  const verifier = result.external_verification || result.external_verifier || {};
  
  if (verifier.threat_intelligence_match) {
    details.push(`<i class="fas fa-shield-virus"></i> Flagged by external threat intelligence`);
  }
  
  // Show consensus if available
  if (verifier.external_consensus && verifier.external_consensus !== 'not_checked') {
    const consensusText = verifier.external_consensus === 'threat' ? 'Threat Detected' : 
                         verifier.external_consensus === 'safe' ? 'Verified Safe' : 'Mixed Results';
    details.push(`<i class="fas fa-balance-scale"></i> External Consensus: ${consensusText}`);
  }
  
  // Add details to list
  details.forEach(detail => {
    const li = document.createElement('li');
    li.innerHTML = detail;
    detailsList.appendChild(li);
  });
  
  // If no specific details, add generic message
  if (details.length === 3 && !isPhishing) {
    const li = document.createElement('li');
    li.innerHTML = '<i class="fas fa-check-circle"></i> No suspicious patterns detected';
    detailsList.appendChild(li);
  }
  
  // Populate Security Details Panel
  updateSecurityDetails(result);
  
  // Populate URL Structure Panel
  updateURLStructure(result);
  
  // Populate External Verification Panel
  updateExternalVerification(result);
  
  // Legacy code for old UI elements (if they still exist)
  const riskScoreElement = document.getElementById('riskScore');
  const riskProgressElement = document.getElementById('riskProgress');
  
  if (riskScoreElement && riskProgressElement) {
    riskScoreElement.textContent = confidence;
    riskProgressElement.style.width = `${confidence}%`;
    
    if (riskLevel === 'high') {
      riskProgressElement.style.backgroundColor = '#dc3545';
    } else if (riskLevel === 'medium') {
      riskProgressElement.style.backgroundColor = '#ffc107';
    } else {
      riskProgressElement.style.backgroundColor = '#28a745';
    }
  }
  
  const flaggedReasons = document.getElementById('flaggedReasons');
  if (flaggedReasons && result.features) {
    flaggedReasons.innerHTML = '';
    
    const reasons = [];
    
    if (isPhishing) {
      if (result.features.suspicious_keywords > 0) {
        reasons.push('Contains suspicious keywords (login, verify, account, etc.)');
      }
      if (result.features.has_ip_address) {
        reasons.push('Uses IP address instead of domain name');
      }
      if (result.url_structure?.length > 75) {
        reasons.push('Unusually long URL');
      }
      if (result.features.dots_in_domain > 3) {
        reasons.push('Excessive dots in domain name');
      }
      if (result.features.has_at_symbol) {
        reasons.push('Contains @ symbol (URL obfuscation)');
      }
      if (result.features.has_double_slash) {
        reasons.push('Contains double slashes (possible redirect)');
      }
      if (result.features.subdomain_count > 2) {
        reasons.push(`Multiple subdomains (${result.features.subdomain_count} found)`);
      }
    }
    
    // If no specific reasons but still flagged, show generic message
    if (reasons.length === 0 && isPhishing) {
      reasons.push('ML model detected phishing patterns');
      reasons.push(`Confidence score: ${confidence}%`);
    }
    
    // Add reasons to the list
    reasons.forEach(reason => {
      const li = document.createElement('li');
      li.textContent = reason;
      flaggedReasons.appendChild(li);
    });
    
    // Show/hide dropdown based on whether it's phishing
    const flaggedDropdown = document.querySelector('.flagged-dropdown');
    if (flaggedDropdown) {
      flaggedDropdown.style.display = isPhishing ? 'block' : 'none';
    }
  }
  
  // Update stats
  loadStats();
}

/**
 * Handle page scan
 */
async function handlePageScan() {
  try {
    // Show loading state
    scanPageBtn.disabled = true;
    scanPageBtn.querySelector('.btn-text').textContent = 'Scanning...';
    pageLoader.style.display = 'inline-block';
    pageStats.style.display = 'none';
    
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.id) {
      showNotification('Cannot scan this page', 'error');
      return;
    }
    
    // Send message to content script to scan page
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'scanPage'
    });
    
    if (response && response.success) {
      showNotification('Page scan completed', 'success');
      
      // Get actual scan results from content script
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          chrome.tabs.sendMessage(tabs[0].id, {action: "getScanResults"}, function(response) {
              if (response && response.results) {
                  displayScanResults(response.results);
              }
          });
      });
      pageStats.style.display = 'flex';
      totalLinks.textContent = '0';
      threatsFound.textContent = '0';
      
      // Reload stats
      await loadStats();
    }
    
  } catch (error) {
    console.error('[TrustLink] Page scan error:', error);
    showNotification('Page scan failed', 'error');
  } finally {
    // Reset loading state
    scanPageBtn.disabled = false;
    scanPageBtn.querySelector('.btn-text').textContent = 'Scan All Links';
    pageLoader.style.display = 'none';
  }
}

/**
 * Validate URL format
 */
function isValidUrl(url) {
  try {
    // Add protocol if missing
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://' + url;
    }
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#667eea'};
    color: white;
    padding: 12px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    animation: slideDown 0.3s ease-out;
  `;
  
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideUp 0.3s ease-out';
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideDown {
    from {
      transform: translateX(-50%) translateY(-20px);
      opacity: 0;
    }
    to {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }
  }
  
  @keyframes slideUp {
    from {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }
    to {
      transform: translateX(-50%) translateY(-20px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

/**
 * Handle paste and scan
 */
async function handlePasteAndScan() {
  try {
    const text = await navigator.clipboard.readText();
    if (text && text.trim()) {
      urlInput.value = text.trim();
      await handleQuickScan();
    } else {
      showNotification('No URL found in clipboard', 'warning');
    }
  } catch (error) {
    console.error('[TrustLink] Clipboard error:', error);
    showNotification('Unable to read clipboard. Please paste manually.', 'error');
  }
}

/**
 * Handle scan current URL
 */
async function handleScanCurrentUrl() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url) {
      showNotification('Unable to get current page URL', 'error');
      return;
    }
    
    // Check if it's a valid URL to scan
    if (tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
      showNotification('Cannot scan browser internal pages', 'warning');
      return;
    }
    
    // Set URL in input and scan
    urlInput.value = tab.url;
    await handleQuickScan();
    
  } catch (error) {
    console.error('[TrustLink] Error scanning current URL:', error);
    showNotification('Failed to scan current page', 'error');
  }
}

/**
 * Update page stats display
 */
function updatePageStats(stats) {
  if (stats && pageStats) {
    totalLinks.textContent = stats.total || 0;
    threatsFound.textContent = stats.threats || 0;
    
    const safeLinksEl = document.getElementById('safeLinks');
    if (safeLinksEl) {
      safeLinksEl.textContent = (stats.total - stats.threats) || 0;
    }
    
    pageStats.style.display = 'flex';
  }
}

/**
 * Update Security Details Panel
 */
function updateSecurityDetails(result) {
  const panel = document.getElementById('securityDetailsPanel');
  if (!panel) return;
  
  const urlStructure = result.url_structure || {};
  const securityInfo = result.security_info || {};
  const domainInfo = result.domain_info || {};
  
  // HTTPS Status
  const httpsIcon = document.getElementById('httpsIcon');
  const httpsStatus = document.getElementById('httpsStatus');
  if (urlStructure.is_https) {
    httpsStatus.textContent = 'Enabled';
    httpsStatus.style.color = 'var(--success-green)';
    httpsIcon.classList.add('success');
  } else {
    httpsStatus.textContent = 'Not Enabled';
    httpsStatus.style.color = 'var(--danger-red)';
    httpsIcon.classList.add('danger');
  }
  
  // SSL Certificate
  const sslIcon = document.getElementById('sslIcon');
  const sslStatus = document.getElementById('sslStatus');
  if (securityInfo.has_valid_ssl) {
    const issuer = securityInfo.ssl_issuer || 'Unknown';
    const daysUntilExpiry = securityInfo.ssl_days_until_expiry;
    if (daysUntilExpiry > 30) {
      sslStatus.textContent = `Valid (${issuer})`;
      sslStatus.style.color = 'var(--success-green)';
      sslIcon.classList.add('success');
    } else if (daysUntilExpiry > 0) {
      sslStatus.textContent = `Expires in ${daysUntilExpiry}d`;
      sslStatus.style.color = 'var(--warning-orange)';
      sslIcon.classList.add('warning');
    } else {
      sslStatus.textContent = 'Valid';
      sslStatus.style.color = 'var(--success-green)';
      sslIcon.classList.add('success');
    }
  } else {
    sslStatus.textContent = 'Invalid/Missing';
    sslStatus.style.color = 'var(--danger-red)';
    sslIcon.classList.add('danger');
  }
  
  // Domain Age
  const domainAgeIcon = document.getElementById('domainAgeIcon');
  const domainAge = document.getElementById('domainAge');
  const domainAgeDays = domainInfo.domain_age_days || -1;
  const domainAgeReadable = urlStructure.domain_age_readable || 'Unknown';
  
  if (domainAgeDays > 730) {
    domainAge.textContent = domainAgeReadable;
    domainAge.style.color = 'var(--success-green)';
    domainAgeIcon.classList.add('success');
  } else if (domainAgeDays > 180) {
    domainAge.textContent = domainAgeReadable;
    domainAge.style.color = 'var(--warning-orange)';
    domainAgeIcon.classList.add('warning');
  } else if (domainAgeDays >= 0) {
    domainAge.textContent = domainAgeReadable;
    domainAge.style.color = 'var(--danger-red)';
    domainAgeIcon.classList.add('danger');
  } else {
    domainAge.textContent = 'Unknown';
    domainAge.style.color = 'var(--text-dim)';
  }
  
  // DNS Records
  const dnsIcon = document.getElementById('dnsIcon');
  const dnsStatus = document.getElementById('dnsStatus');
  const hasDNS = domainInfo.has_dns_record;
  const hasMX = domainInfo.has_mx_record;
  
  if (hasDNS && hasMX) {
    dnsStatus.textContent = 'Complete';
    dnsStatus.style.color = 'var(--success-green)';
    dnsIcon.classList.add('success');
  } else if (hasDNS) {
    dnsStatus.textContent = 'Partial';
    dnsStatus.style.color = 'var(--warning-orange)';
    dnsIcon.classList.add('warning');
  } else {
    dnsStatus.textContent = 'Missing';
    dnsStatus.style.color = 'var(--danger-red)';
    dnsIcon.classList.add('danger');
  }
  
  panel.style.display = 'block';
}

/**
 * Update URL Structure Panel
 */
function updateURLStructure(result) {
  const panel = document.getElementById('urlStructurePanel');
  if (!panel) return;
  
  const urlStructure = result.url_structure || {};
  const features = result.features || {};
  
  // Protocol
  const urlProtocol = document.getElementById('urlProtocol');
  if (urlProtocol) {
    urlProtocol.textContent = (urlStructure.protocol || 'http').toUpperCase();
    urlProtocol.style.color = urlStructure.is_https ? 'var(--success-green)' : 'var(--warning-orange)';
  }
  
  // Domain
  const urlDomain = document.getElementById('urlDomain');
  if (urlDomain) {
    urlDomain.textContent = urlStructure.domain || 'Unknown';
  }
  
  // Subdomains
  const subdomainCount = document.getElementById('subdomainCount');
  if (subdomainCount) {
    const count = features.num_subdomains || 0;
    subdomainCount.textContent = count;
    subdomainCount.style.color = count > 2 ? 'var(--warning-orange)' : 'var(--text-primary)';
  }
  
  // Path Length
  const pathLength = document.getElementById('pathLength');
  if (pathLength) {
    const length = urlStructure.path_length || 0;
    pathLength.textContent = length + ' chars';
    pathLength.style.color = length > 50 ? 'var(--warning-orange)' : 'var(--text-primary)';
  }
  
  panel.style.display = 'block';
}

/**
 * Update External Verification Panel
 */
function updateExternalVerification(result) {
  const panel = document.getElementById('externalVerificationPanel');
  if (!panel) return;
  
  // Check both field names for compatibility
  const verification = result.external_verification || result.external_verifier || {};
  const verifiersConsulted = verification.verifiers_consulted || [];
  const consensus = verification.external_consensus || 'not_checked';
  const isThreat = verification.threat_intelligence_match;
  const externalConfidence = verification.confidence_from_external || 0;
  
  // Check if any verifiers were used
  const hasGoogleCheck = verifiersConsulted.includes('google') || verifiersConsulted.includes('Google Safe Browsing');
  const hasVirusTotalCheck = verifiersConsulted.includes('virustotal') || verifiersConsulted.includes('VirusTotal');
  const hasPhishTankCheck = verifiersConsulted.includes('phishtank') || verifiersConsulted.includes('PhishTank');
  
  // VirusTotal
  const virusTotalItem = document.getElementById('virusTotalItem');
  const virusTotalStatus = document.getElementById('virusTotalStatus');
  if (hasVirusTotalCheck) {
    if (consensus === 'threat' && isThreat) {
      virusTotalStatus.textContent = `VirusTotal: Flagged`;
      virusTotalStatus.style.color = 'var(--danger-red)';
      virusTotalItem.classList.add('flagged');
    } else if (consensus === 'safe' && !isThreat) {
      virusTotalStatus.textContent = 'VirusTotal: Clean';
      virusTotalStatus.style.color = 'var(--success-green)';
      virusTotalItem.classList.add('verified');
    } else {
      virusTotalStatus.textContent = 'VirusTotal: Checked';
      virusTotalStatus.style.color = 'var(--text-secondary)';
    }
  } else {
    virusTotalStatus.textContent = 'VirusTotal: Not Checked';
    virusTotalStatus.style.color = 'var(--text-dim)';
  }
  
  // Google Safe Browsing
  const safeBrowsingItem = document.getElementById('safeBrowsingItem');
  const safeBrowsingStatus = document.getElementById('safeBrowsingStatus');
  if (hasGoogleCheck) {
    if (consensus === 'threat' && isThreat) {
      safeBrowsingStatus.textContent = 'Google Safe Browsing: Flagged';
      safeBrowsingStatus.style.color = 'var(--danger-red)';
      safeBrowsingItem.classList.add('flagged');
    } else if (consensus === 'safe' && !isThreat) {
      safeBrowsingStatus.textContent = 'Google Safe Browsing: Clean';
      safeBrowsingStatus.style.color = 'var(--success-green)';
      safeBrowsingItem.classList.add('verified');
    } else {
      safeBrowsingStatus.textContent = 'Google Safe Browsing: Checked';
      safeBrowsingStatus.style.color = 'var(--text-secondary)';
    }
  } else {
    safeBrowsingStatus.textContent = 'Google Safe Browsing: Not Checked';
    safeBrowsingStatus.style.color = 'var(--text-dim)';
  }
  
  // PhishTank
  const phishTankItem = document.getElementById('phishTankItem');
  const phishTankStatus = document.getElementById('phishTankStatus');
  if (hasPhishTankCheck) {
    if (consensus === 'threat' && isThreat) {
      phishTankStatus.textContent = 'PhishTank: Found in Database';
      phishTankStatus.style.color = 'var(--danger-red)';
      phishTankItem.classList.add('flagged');
    } else if (consensus === 'safe' && !isThreat) {
      phishTankStatus.textContent = 'PhishTank: Not in Database';
      phishTankStatus.style.color = 'var(--success-green)';
      phishTankItem.classList.add('verified');
    } else {
      phishTankStatus.textContent = 'PhishTank: Checked';
      phishTankStatus.style.color = 'var(--text-secondary)';
    }
  } else {
    phishTankStatus.textContent = 'PhishTank: Not Checked';
    phishTankStatus.style.color = 'var(--text-dim)';
  }
  
  // Show panel if any verification was performed
  if (verifiersConsulted.length > 0 || consensus !== 'not_checked') {
    panel.style.display = 'block';
  }
}

console.log('[TrustLink] Popup initialized');

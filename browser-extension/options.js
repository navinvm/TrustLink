/**
 * TrustLink Browser Extension - Options Page Script
 */

// Default configuration
const DEFAULT_CONFIG = {
  apiUrl: '',  // Set this in the extension options page
  apiKey: '',
  enableRealTimeScanning: true,
  scanDelay: 500,
  cacheEnabled: true,
  cacheDuration: 86400000,
  confidenceThreshold: 50,
  showSafeIndicators: true,
  autoScanOnPageLoad: true
};

let currentConfig = { ...DEFAULT_CONFIG };

// DOM Elements
const apiUrlInput = document.getElementById('apiUrl');
const apiKeyInput = document.getElementById('apiKey');
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const testConnectionBtn = document.getElementById('testConnection');
const connectionStatus = document.getElementById('connectionStatus');

const enableRealTimeScanning = document.getElementById('enableRealTimeScanning');
const autoScanOnPageLoad = document.getElementById('autoScanOnPageLoad');
const scanDelaySlider = document.getElementById('scanDelay');
const scanDelayValue = document.getElementById('scanDelayValue');
const confidenceThresholdSlider = document.getElementById('confidenceThreshold');
const confidenceThresholdValue = document.getElementById('confidenceThresholdValue');

const showSafeIndicators = document.getElementById('showSafeIndicators');
const cacheEnabled = document.getElementById('cacheEnabled');
const cacheDurationSelect = document.getElementById('cacheDuration');
const clearCacheBtn = document.getElementById('clearCache');
const cacheStats = document.getElementById('cacheStats');

const resetDefaultsBtn = document.getElementById('resetDefaults');
const saveSettingsBtn = document.getElementById('saveSettings');
const saveStatus = document.getElementById('saveStatus');

const dashboardLink = document.getElementById('dashboardLink');

// Initialize
(async function init() {
  try {
    // Load current configuration
    const response = await chrome.runtime.sendMessage({ action: 'getConfig' });
    if (response) {
      currentConfig = { ...DEFAULT_CONFIG, ...response };
    }
    
    // Populate form
    populateForm();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load cache stats
    loadCacheStats();
    
  } catch (error) {
    console.error('[TrustLink] Options initialization error:', error);
  }
})();

/**
 * Populate form with current configuration
 */
function populateForm() {
  apiUrlInput.value = currentConfig.apiUrl;
  apiKeyInput.value = currentConfig.apiKey;
  
  enableRealTimeScanning.checked = currentConfig.enableRealTimeScanning;
  autoScanOnPageLoad.checked = currentConfig.autoScanOnPageLoad;
  
  scanDelaySlider.value = currentConfig.scanDelay;
  scanDelayValue.textContent = `${currentConfig.scanDelay}ms`;
  
  confidenceThresholdSlider.value = currentConfig.confidenceThreshold;
  confidenceThresholdValue.textContent = `${currentConfig.confidenceThreshold}%`;
  
  showSafeIndicators.checked = currentConfig.showSafeIndicators;
  cacheEnabled.checked = currentConfig.cacheEnabled;
  cacheDurationSelect.value = currentConfig.cacheDuration.toString();
  
  // Set dashboard link
  dashboardLink.href = `${currentConfig.apiUrl}/dashboard`;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Toggle API key visibility
  toggleApiKeyBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      toggleApiKeyBtn.textContent = 'Hide';
    } else {
      apiKeyInput.type = 'password';
      toggleApiKeyBtn.textContent = 'Show';
    }
  });
  
  // Test connection
  testConnectionBtn.addEventListener('click', testConnection);
  
  // Slider updates
  scanDelaySlider.addEventListener('input', (e) => {
    scanDelayValue.textContent = `${e.target.value}ms`;
  });
  
  confidenceThresholdSlider.addEventListener('input', (e) => {
    confidenceThresholdValue.textContent = `${e.target.value}%`;
  });
  
  // Clear cache
  clearCacheBtn.addEventListener('click', async () => {
    if (confirm('Clear all cached scan results?')) {
      await chrome.runtime.sendMessage({ action: 'clearCache' });
      showSaveStatus('Cache cleared successfully', 'success');
      loadCacheStats();
    }
  });
  
  // Reset defaults
  resetDefaultsBtn.addEventListener('click', () => {
    if (confirm('Reset all settings to defaults?')) {
      currentConfig = { ...DEFAULT_CONFIG };
      populateForm();
      showSaveStatus('Settings reset to defaults. Click Save to apply.', 'info');
    }
  });
  
  // Save settings
  saveSettingsBtn.addEventListener('click', saveSettings);
  
  // Dashboard link
  dashboardLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: dashboardLink.href });
  });
}

/**
 * Test API connection
 */
async function testConnection() {
  const apiUrl = apiUrlInput.value.trim();
  const apiKey = apiKeyInput.value.trim();
  
  if (!apiUrl) {
    showConnectionStatus('Please enter an API URL', 'error');
    return;
  }
  
  testConnectionBtn.disabled = true;
  testConnectionBtn.textContent = 'Testing...';
  
  try {
    const endpoint = `${apiUrl}/health`;
    const response = await fetch(endpoint);
    
    if (response.ok) {
      const data = await response.json();
      showConnectionStatus(
        `Connection successful! Model loaded: ${data.model_loaded}`,
        'success'
      );
    } else {
      showConnectionStatus(`Connection failed: ${response.status}`, 'error');
    }
  } catch (error) {
    showConnectionStatus(`Connection failed: ${error.message}`, 'error');
  } finally {
    testConnectionBtn.disabled = false;
    testConnectionBtn.innerHTML = '<span>Test Connection</span>';
  }
}

/**
 * Save settings
 */
async function saveSettings() {
  try {
    // Gather configuration from form
    const newConfig = {
      apiUrl: apiUrlInput.value.trim(),
      apiKey: apiKeyInput.value.trim(),
      enableRealTimeScanning: enableRealTimeScanning.checked,
      autoScanOnPageLoad: autoScanOnPageLoad.checked,
      scanDelay: parseInt(scanDelaySlider.value),
      confidenceThreshold: parseInt(confidenceThresholdSlider.value),
      showSafeIndicators: showSafeIndicators.checked,
      cacheEnabled: cacheEnabled.checked,
      cacheDuration: parseInt(cacheDurationSelect.value)
    };
    
    // Validate
    if (!newConfig.apiUrl) {
      showSaveStatus('API URL is required', 'error');
      return;
    }
    
    // Save to background
    saveSettingsBtn.disabled = true;
    saveSettingsBtn.innerHTML = '<span>Saving...</span>';
    
    await chrome.runtime.sendMessage({
      action: 'updateConfig',
      config: newConfig
    });
    
    currentConfig = newConfig;
    
    // Notify content scripts of config update
    const tabs = await chrome.tabs.query({});
    for (const tab of tabs) {
      try {
        await chrome.tabs.sendMessage(tab.id, {
          action: 'configUpdated',
          config: newConfig
        });
      } catch (e) {
        // Tab may not have content script
      }
    }
    
    showSaveStatus('Settings saved successfully!', 'success');
    
  } catch (error) {
    console.error('[TrustLink] Save error:', error);
    showSaveStatus('Failed to save settings', 'error');
  } finally {
    saveSettingsBtn.disabled = false;
    saveSettingsBtn.innerHTML = '<span>Save Settings</span>';
  }
}

/**
 * Load cache statistics
 */
async function loadCacheStats() {
  try {
    const stats = await chrome.runtime.sendMessage({ action: 'getCacheStats' });
    
    if (stats) {
      cacheStats.innerHTML = `
        <strong>Cache Statistics:</strong><br>
        Total entries: ${stats.total}<br>
        Valid entries: ${stats.valid}<br>
        Expired entries: ${stats.expired}
      `;
      cacheStats.style.display = 'block';
    }
  } catch (error) {
    console.error('[TrustLink] Error loading cache stats:', error);
  }
}

/**
 * Show connection status message
 */
function showConnectionStatus(message, type) {
  connectionStatus.textContent = message;
  connectionStatus.className = `status-message ${type}`;
  connectionStatus.style.display = 'block';
  
  setTimeout(() => {
    connectionStatus.style.display = 'none';
  }, 5000);
}

/**
 * Show save status message
 */
function showSaveStatus(message, type) {
  saveStatus.textContent = message;
  saveStatus.className = `save-status ${type}`;
  saveStatus.style.display = 'block';
  
  setTimeout(() => {
    saveStatus.style.display = 'none';
  }, 5000);
}

console.log('[TrustLink] Options page initialized');

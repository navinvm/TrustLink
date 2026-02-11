/**
 * TrustLink Browser Extension - Background Service Worker
 * Handles API communication and caching
 */

// Default configuration
const DEFAULT_CONFIG = {
  apiUrl: 'http://localhost:5000',  // Default to local TrustLink server
  apiKey: '',
  enableRealTimeScanning: true,
  scanDelay: 500, // ms delay before scanning
  cacheEnabled: true,
  cacheDuration: 86400000, // 24 hours in ms
  confidenceThreshold: 50, // Show warnings for confidence > 50%
  showSafeIndicators: true,
  autoScanOnPageLoad: true,
  safeMode: false, // Safe mode: blocks dangerous links automatically
  safeModeStrength: 'medium' // low, medium, high
};

// Cache for scan results (in-memory for performance)
let scanCache = new Map();
let config = { ...DEFAULT_CONFIG };

// Debounce cache saves to reduce storage writes
let cacheSaveTimeout = null;
const debouncedCacheSave = () => {
  if (cacheSaveTimeout) clearTimeout(cacheSaveTimeout);
  cacheSaveTimeout = setTimeout(async () => {
    const cacheObj = Object.fromEntries(scanCache);
    await chrome.storage.local.set({ scanCache: cacheObj });
  }, 2000); // Save after 2 seconds of inactivity
};

// Initialize extension
chrome.runtime.onInstalled.addListener(async () => {
  console.log('TrustLink extension installed');
  
  // Load saved configuration
  const saved = await chrome.storage.local.get(['config', 'scanCache']);
  if (saved.config) {
    config = { ...DEFAULT_CONFIG, ...saved.config };
  }
  if (saved.scanCache) {
    scanCache = new Map(Object.entries(saved.scanCache));
  }
  
  // Set default config if not exists
  await chrome.storage.local.set({ config });
});

// Load configuration on startup
chrome.runtime.onStartup.addListener(async () => {
  const saved = await chrome.storage.local.get(['config', 'scanCache']);
  if (saved.config) {
    config = { ...DEFAULT_CONFIG, ...saved.config };
  }
  if (saved.scanCache) {
    scanCache = new Map(Object.entries(saved.scanCache));
  }
});

/**
 * Scan a URL using TrustLink API
 */
async function scanUrl(url) {
  try {
    // Check cache first (using Map for better performance)
    if (config.cacheEnabled && scanCache.has(url)) {
      const cached = scanCache.get(url);
      const age = Date.now() - cached.timestamp;
      
      if (age < config.cacheDuration) {
        console.log(`[TrustLink] Cache hit for ${url}`);
        return { ...cached.result, cached: true };
      } else {
        // Cache expired
        scanCache.delete(url);
      }
    }
    
    // Prepare API request
    const endpoint = `${config.apiUrl}/predict`;
    const headers = {
      'Content-Type': 'application/json'
    };
    
    // Add API key if configured
    if (config.apiKey) {
      headers['X-API-Key'] = config.apiKey;
    }
    
    // Make API request with timeout - same endpoint as website
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ 
          url: url,
          source: 'extension' // Identify requests from extension
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error (${response.status}): ${errorText || 'Server error'}`);
      }
      
      const result = await response.json();
      
      // Cache the result
      if (config.cacheEnabled) {
        scanCache.set(url, {
          result: result,
          timestamp: Date.now()
        });
        
        // Clean old cache entries (keep last 1000)
        if (scanCache.size > 1000) {
          const entries = Array.from(scanCache.entries())
            .sort((a, b) => a[1].timestamp - b[1].timestamp);
          
          // Remove oldest 200 entries
          for (let i = 0; i < 200; i++) {
            scanCache.delete(entries[i][0]);
          }
        }
        
        // Debounced save cache to storage
        debouncedCacheSave();
      }
      
      return { ...result, cached: false };
      
    } catch (fetchError) {
      clearTimeout(timeoutId);
      
      // Provide more helpful error messages
      if (fetchError.name === 'AbortError') {
        throw new Error('Request timeout - Server took too long to respond');
      } else if (fetchError.message.includes('Failed to fetch')) {
        throw new Error(`Cannot connect to TrustLink server at ${config.apiUrl}. Please check:\n1. Is the server running?\n2. Is the API URL correct in extension options?\n3. Check your internet connection.`);
      } else {
        throw fetchError;
      }
    }
    
  } catch (error) {
    console.error('[TrustLink] Scan error:', error);
    
    // Return user-friendly error
    let errorMessage = error.message;
    
    // Check for common issues
    if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Cannot connect')) {
      errorMessage = `Server Connection Failed\n\nThe TrustLink server (${config.apiUrl}) is not responding.\n\nPlease:\n• Make sure the server is running\n• Check the API URL in extension settings\n• Verify your internet connection`;
    } else if (errorMessage.includes('NetworkError')) {
      errorMessage = 'Network error - Please check your internet connection';
    } else if (errorMessage.includes('CORS')) {
      errorMessage = 'Server configuration error - CORS not enabled. Please contact administrator.';
    }
    
    return {
      status: 'error',
      error: errorMessage,
      url: url
    };
  }
}

/**
 * Batch scan multiple URLs
 */
async function batchScanUrls(urls) {
  try {
    // Filter out already cached URLs
    const uncachedUrls = [];
    const results = {};
    
    for (const url of urls) {
      if (config.cacheEnabled && scanCache.has(url)) {
        const cached = scanCache.get(url);
        const age = Date.now() - cached.timestamp;
        
        if (age < config.cacheDuration) {
          results[url] = { ...cached.result, cached: true };
        } else {
          uncachedUrls.push(url);
          scanCache.delete(url);
        }
      } else {
        uncachedUrls.push(url);
      }
    }
    
    // If all URLs were cached, return immediately
    if (uncachedUrls.length === 0) {
      return results;
    }
    
    // Batch scan uncached URLs
    const endpoint = config.apiKey 
      ? `${config.apiUrl}/api/v1/batch-scan`
      : `${config.apiUrl}/predict`;
    
    if (config.apiKey && uncachedUrls.length > 1) {
      // Use batch endpoint if we have API key
      const headers = {
        'Content-Type': 'application/json',
        'X-API-Key': config.apiKey
      };
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ 
          urls: uncachedUrls,
          source: 'extension' // Identify requests from extension
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.results) {
          for (const item of data.results) {
            if (item.status === 'success') {
              results[item.url] = { ...item, cached: false };
              
              // Cache the result
              if (config.cacheEnabled) {
                scanCache.set(item.url, {
                  result: item,
                  timestamp: Date.now()
                });
              }
            }
          }
        }
      }
    } else {
      // Scan individually (no batch support or no API key)
      for (const url of uncachedUrls) {
        const result = await scanUrl(url);
        results[url] = result;
      }
    }
    
    // Save cache (debounced)
    if (config.cacheEnabled) {
      debouncedCacheSave();
    }
    
    return results;
    
  } catch (error) {
    console.error('[TrustLink] Batch scan error:', error);
    return {};
  }
}

/**
 * Get current configuration
 */
async function getConfig() {
  return config;
}

/**
 * Update configuration
 */
async function updateConfig(newConfig) {
  config = { ...config, ...newConfig };
  await chrome.storage.local.set({ config });
  return config;
}

/**
 * Clear cache
 */
async function clearCache() {
  scanCache.clear();
  await chrome.storage.local.set({ scanCache: {} });
  return { success: true, message: 'Cache cleared' };
}

/**
 * Get cache statistics
 */
function getCacheStats() {
  const now = Date.now();
  let validCount = 0;
  
  for (const [, cached] of scanCache) {
    const age = now - cached.timestamp;
    if (age < config.cacheDuration) {
      validCount++;
    }
  }
  
  return {
    total: scanCache.size,
    valid: validCount,
    expired: scanCache.size - validCount
  };
}

// Message handler for communication with content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[TrustLink] Message received:', request.action);
  
  switch (request.action) {
    case 'scanUrl':
      scanUrl(request.url).then(sendResponse);
      return true; // Keep channel open for async response
      
    case 'batchScan':
      batchScanUrls(request.urls).then(sendResponse);
      return true;
      
    case 'getConfig':
      getConfig().then(sendResponse);
      return true;
      
    case 'updateConfig':
      updateConfig(request.config).then(sendResponse);
      return true;
      
    case 'clearCache':
      clearCache().then(sendResponse);
      return true;
      
    case 'getCacheStats':
      sendResponse(getCacheStats());
      return false;
      
    case 'logSafeModeOverride':
      // Log when user overrides safe mode blocking
      console.warn('[TrustLink Safe Mode] User overrode protection for:', request.url, 'Risk Level:', request.riskLevel);
      // Could send to analytics/tracking service here
      sendResponse({ logged: true });
      return false;
      
    default:
      sendResponse({ error: 'Unknown action' });
      return false;
  }
});

// Update badge with scan count
let scanCount = 0;
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateBadge') {
    scanCount = request.count || 0;
    if (scanCount > 0) {
      chrome.action.setBadgeText({ text: scanCount.toString() });
      chrome.action.setBadgeBackgroundColor({ color: '#dc3545' });
    } else {
      chrome.action.setBadgeText({ text: '' });
    }
  }
});

// Listen for keyboard commands
chrome.commands.onCommand.addListener(async (command) => {
  console.log('[TrustLink] Command received:', command);
  
  if (command === 'scan-current-page') {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.url) {
        // Check if valid URL
        if (tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
          console.log('[TrustLink] Cannot scan browser internal pages');
          return;
        }
        
        // Scan the URL
        const result = await scanUrl(tab.url);
        
        // Show notification with result
        const isPhishing = result.prediction === 'Phishing';
        const title = isPhishing ? '⚠️ Phishing Detected!' : '✅ Safe URL';
        const message = isPhishing 
          ? `This page may be dangerous (${result.confidence}% confidence)`
          : `This page appears safe (${result.confidence}% confidence)`;
        
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon128.png',
          title: title,
          message: message,
          priority: 2
        });
        
        // Update badge
        updateBadge(result);
      }
    } catch (error) {
      console.error('[TrustLink] Error executing scan command:', error);
    }
  }
});

console.log('[TrustLink] Background service worker initialized');

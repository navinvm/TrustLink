# 🌐 TrustLink Browser Extension Guide

## Overview

The TrustLink Browser Extension brings **real-time phishing protection** directly to your browser! It automatically scans links as you browse and alerts you to potential threats before you click.

## 🎯 What It Does

### Real-Time Protection
- **Automatic Scanning**: Scans all links on web pages as they load
- **Instant Detection**: New links added dynamically are detected immediately
- **Visual Warnings**: Color-coded indicators show risk level at a glance
- **Click Protection**: Dangerous links show confirmation dialog before opening

### How It Works

1. **You browse normally** → Visit any website
2. **Extension scans** → All links are automatically analyzed
3. **Visual feedback** → Links are marked with color indicators:
   - 🛑 **Red** = Danger (phishing detected)
   - ⚠️ **Yellow** = Warning (suspicious)
   - ✓ **Green** = Safe (verified)
4. **Click protection** → Dangerous links show warning before opening

## 📁 Extension Structure

```
browser-extension/
├── manifest.json           # Extension configuration
├── background.js          # Service worker (API communication)
├── content.js            # Content script (page scanning)
├── content.css           # Visual indicators styling
├── popup.html            # Extension popup UI
├── popup.js              # Popup functionality
├── popup.css             # Popup styling
├── options.html          # Settings page
├── options.js            # Settings functionality
├── options.css           # Settings styling
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
├── README.md             # Usage documentation
└── INSTALLATION.md       # Installation guide
```

## 🚀 Quick Start

### 1. Install the Extension

**Chrome/Edge/Brave:**
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `browser-extension` folder

**Firefox:**
1. Open `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `browser-extension/manifest.json`

### 2. Start TrustLink Backend

```bash
cd /path/to/trustlink
python app.py
```

The backend should be running on `http://localhost:5000`

### 3. Configure Extension

1. Click the TrustLink icon in your toolbar
2. Click "⚙️ Settings"
3. Enter API URL: `http://localhost:5000`
4. Click "Test Connection"
5. Click "Save Settings"

### 4. Start Browsing!

The extension is now protecting you! Visit any website and links will be automatically scanned.

## 🎨 Visual Indicators Explained

### 🛑 Red - DANGER
- **What it means**: High-confidence phishing detection
- **What you see**: Red background, strikethrough text, pulsing 🛑 icon
- **What happens**: Clicking shows warning dialog with risk details
- **Action**: **DO NOT CLICK** - Link is very likely malicious

### ⚠️ Yellow - WARNING
- **What it means**: Suspicious link, potential threat
- **What you see**: Yellow background, ⚠️ warning icon
- **What happens**: Link works normally but be cautious
- **Action**: Proceed with caution, review URL carefully

### ✓ Green - SAFE
- **What it means**: Verified safe link
- **What you see**: Subtle green checkmark
- **What happens**: Link works normally
- **Action**: Safe to click

### Tooltips
Hover over any scanned link to see:
- Verdict (Safe/Phishing)
- Confidence percentage
- Risk level

## 📋 Features Detail

### Automatic Scanning
- **On Page Load**: All links scanned when page finishes loading
- **Dynamic Content**: New links detected as they're added (AJAX, React, etc.)
- **Configurable Delay**: Set delay before scanning (reduces overhead)

### Smart Caching
- **Results Cached**: Scan results stored locally to reduce API calls
- **Configurable Duration**: Set cache lifetime (1 hour to 7 days)
- **Automatic Cleanup**: Old cache entries removed automatically
- **Manual Clear**: Clear cache anytime from settings

### Batch Processing
- **Efficient**: Multiple links scanned together (with API key)
- **Throttled**: Prevents overwhelming the API
- **Background**: Scanning happens without blocking page load

### API Integration
- **Flexible Endpoint**: Connect to any TrustLink instance
- **Optional API Key**: For authenticated access and advanced features
- **Health Check**: Test connection before saving settings
- **Error Handling**: Graceful fallback if API unavailable

## ⚙️ Configuration Options

### Connection Settings
- **API URL**: TrustLink backend address (default: `http://localhost:5000`)
- **API Key**: Optional for authenticated access and batch scanning

### Scanning Settings
- **Enable Real-Time Scanning**: Turn automatic scanning on/off
- **Auto-Scan on Page Load**: Scan all links when page loads
- **Scan Delay**: Delay before scanning (0-2000ms)
- **Confidence Threshold**: Minimum confidence to show warnings (0-100%)

### Display Settings
- **Show Safe Indicators**: Display checkmarks for safe links (optional)

### Cache Settings
- **Enable Caching**: Turn caching on/off
- **Cache Duration**: How long to keep results (1 hour - 7 days)

## 🎯 Use Cases

### For General Users
- **Browse Safely**: Automatic protection on all websites
- **Email Links**: Scan links in webmail (Gmail, Outlook, etc.)
- **Social Media**: Protect against phishing on Facebook, Twitter, etc.
- **Shopping**: Verify e-commerce links before purchasing

### For Security Teams
- **Team Protection**: Deploy to organization's browsers
- **Central Management**: Connect all extensions to central server
- **Analytics**: Track threats across organization
- **API Keys**: Monitor usage per user

### For Researchers
- **Threat Analysis**: Study phishing campaigns
- **Dataset Collection**: Gather phishing URLs
- **Model Testing**: Test ML model in real-world scenarios
- **Performance**: Measure detection accuracy

## 🔧 Technical Details

### Architecture

```
┌─────────────┐
│   Webpage   │
│   (Links)   │
└──────┬──────┘
       │
       ├─── Content Script (content.js)
       │    • Detects links
       │    • Applies indicators
       │    • Monitors DOM changes
       │
       ▼
┌─────────────────────┐
│ Background Service  │ ◄──── API Request
│   (background.js)   │ ────► TrustLink Backend
│   • Caching         │       (localhost:5000)
│   • Batch scanning  │
│   • API calls       │
└─────────────────────┘
       ▲
       │
┌─────────────┐
│   Popup     │
│ (popup.js)  │
│ • Quick scan│
│ • Stats     │
└─────────────┘
```

### Communication Flow

1. **Content Script** detects links on page
2. **Content Script** sends URLs to **Background Service**
3. **Background Service** checks cache
4. If not cached, **Background Service** calls **TrustLink API**
5. **Background Service** returns results to **Content Script**
6. **Content Script** applies visual indicators

### Performance Optimizations

- **Debouncing**: Delays scanning to batch multiple requests
- **Caching**: Avoids redundant API calls
- **Lazy Loading**: Scans only visible links (optional)
- **Web Workers**: Offloads processing (future enhancement)

## 🛡️ Security & Privacy

### What We Collect
- **URLs Scanned**: Sent to YOUR TrustLink instance
- **Settings**: Stored locally in browser
- **Cache**: Stored locally in browser

### What We DON'T Collect
- ❌ Browsing history
- ❌ Personal information
- ❌ Page content (only link URLs)
- ❌ Analytics or tracking

### Data Flow
- URLs are only sent to the API endpoint YOU configure
- No third-party services (unless you use external API)
- All storage is local (browser's storage API)

## 🐛 Troubleshooting

### Extension Not Working
1. Check extension is enabled in browser
2. Verify TrustLink backend is running
3. Test connection in settings
4. Check console for errors (F12 → Console)

### Links Not Being Scanned
1. Ensure "Real-Time Scanning" is enabled in settings
2. Refresh the page after enabling
3. Click "Scan All Links" manually in popup
4. Check API URL is correct

### Performance Issues
1. Increase scan delay (Settings → 1000ms)
2. Disable auto-scan on page load
3. Reduce cache size
4. Check backend server performance

### False Positives/Negatives
1. Adjust confidence threshold in settings
2. Report feedback through dashboard
3. Retrain ML model with more data
4. Add domains to whitelist

## 📊 Statistics & Monitoring

### Popup Stats
- **Links Scanned**: Total links processed
- **Threats Blocked**: Phishing links detected
- **Cache Size**: Number of cached results

### Per-Page Stats
- **Total Links**: Links found on current page
- **Threats Found**: Dangerous links on page

### Dashboard Integration
- View full scan history in TrustLink Dashboard
- Access analytics and trends
- Manage API keys
- Update whitelist

## 🔄 Updates & Maintenance

### Updating Extension
1. Download new version
2. Remove old extension
3. Load new version
4. Settings are preserved

### Clearing Cache
- Go to Settings → "Clear Cache Now"
- Or uninstall/reinstall extension

### Model Updates
When TrustLink backend model is updated:
1. Clear extension cache
2. Restart backend
3. Test with known URLs

## 🚀 Future Enhancements

Planned features:
- [ ] Offline mode with local ML model
- [ ] Per-site settings (whitelist specific domains)
- [ ] Custom styling themes
- [ ] Export/import settings
- [ ] Safari support
- [ ] Mobile browser support
- [ ] Whitelist management in extension
- [ ] Real-time sync across devices

## 📚 Additional Resources

- **Extension README**: `browser-extension/README.md` - Detailed usage guide
- **Installation Guide**: `browser-extension/INSTALLATION.md` - Step-by-step setup
- **Main Documentation**: `README.md` - TrustLink system overview
- **API Guide**: `API_GUIDE.md` - API endpoints reference

## 🎉 Getting Started

Ready to protect your browsing?

1. ✅ Install the extension ([INSTALLATION.md](browser-extension/INSTALLATION.md))
2. ✅ Configure settings
3. ✅ Browse safely!

**The web is safer with TrustLink! 🛡️**

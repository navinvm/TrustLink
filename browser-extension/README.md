# 🛡️ TrustLink Browser Extension

Real-time phishing protection that works instantly as you browse! The TrustLink browser extension automatically scans links on web pages and alerts you to potential phishing threats before you click.

## ✨ Features

### 🔍 Real-Time Link Scanning
- **Automatic Detection**: Scans all links on web pages as they load
- **Live Updates**: Detects new links added dynamically to pages
- **Instant Warnings**: Visual indicators appear immediately on dangerous links

### 🎨 Visual Indicators
- **🛑 Danger (Red)**: High-confidence phishing detection with strong warning
- **⚠️ Warning (Yellow)**: Suspicious links with medium confidence
- **✓ Safe (Green)**: Verified safe links with high confidence

### 🚫 Click Protection
- **Interactive Warnings**: Confirmation dialog before opening dangerous links
- **Risk Information**: Shows confidence level and risk factors before proceeding
- **Bypass Option**: Users can still proceed if they understand the risk

### ⚡ Performance Optimized
- **Smart Caching**: Caches scan results to reduce API calls (configurable duration)
- **Batch Scanning**: Efficiently scans multiple links at once
- **Minimal Overhead**: Lightweight and fast, won't slow down your browsing

### 🎛️ Highly Configurable
- **Custom API Endpoint**: Connect to your own TrustLink server
- **API Key Support**: Use authenticated API for advanced features
- **Adjustable Thresholds**: Control when warnings appear
- **Display Preferences**: Show or hide safe link indicators
- **Auto-Scan Settings**: Enable/disable automatic scanning

## 🚀 Installation

### Chrome / Edge / Brave

1. **Download the Extension**
   - Clone this repository or download the `browser-extension` folder

2. **Enable Developer Mode**
   - Open Chrome and navigate to `chrome://extensions/`
   - Toggle "Developer mode" in the top-right corner

3. **Load the Extension**
   - Click "Load unpacked"
   - Select the `browser-extension` folder
   - The TrustLink icon should appear in your toolbar

4. **Configure the Extension**
   - Click the TrustLink icon in your toolbar
   - Click "⚙️ Settings"
   - Enter your TrustLink API URL (default: `http://localhost:5000`)
   - Optionally add your API key for authenticated access
   - Click "Save Settings"

### Firefox

1. **Download the Extension**
   - Clone this repository or download the `browser-extension` folder

2. **Load Temporary Extension**
   - Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
   - Click "Load Temporary Add-on"
   - Select the `manifest.json` file in the `browser-extension` folder

3. **Configure the Extension**
   - Click the TrustLink icon in your toolbar
   - Click "⚙️ Settings"
   - Enter your TrustLink API URL
   - Click "Save Settings"

**Note**: For permanent installation in Firefox, the extension needs to be signed by Mozilla.

## ⚙️ Configuration

### Basic Setup

1. **Start TrustLink Backend**
   ```bash
   # From the main TrustLink directory
   python app.py
   ```
   The server will run on `http://localhost:5000` by default.

2. **Configure Extension**
   - Click the TrustLink extension icon
   - Go to Settings (⚙️)
   - Set API URL to `http://localhost:5000`
   - Test the connection
   - Save settings

### Advanced Configuration

#### API Key (Optional)
For authenticated access and advanced features:
1. Log in to TrustLink Dashboard (`http://localhost:5000/login`)
2. Go to API Keys page
3. Generate a new API key
4. Copy the key to extension settings

#### Scanning Settings
- **Real-Time Scanning**: Enable/disable automatic link scanning
- **Auto-Scan on Page Load**: Scan all links when a page loads
- **Scan Delay**: Delay before scanning new links (0-2000ms)
- **Confidence Threshold**: Minimum confidence to show warnings (0-100%)

#### Display Settings
- **Show Safe Indicators**: Display checkmarks for verified safe links
- **Cache Duration**: How long to cache scan results (1 hour - 7 days)

## 📖 Usage Guide

### Automatic Protection

Once installed and configured, TrustLink works automatically:

1. **Browse Normally**: Visit any website
2. **Automatic Scanning**: Links are scanned as pages load
3. **Visual Indicators**: See color-coded warnings on links
4. **Hover for Details**: Hover over links to see tooltip with scan results
5. **Click Protection**: Dangerous links show a warning before opening

### Manual Scanning

#### Quick Scan from Popup
1. Click the TrustLink icon in your toolbar
2. Enter a URL in the "Quick Scan" field
3. Click "Scan URL"
4. View detailed results

#### Scan Current Page
1. Click the TrustLink icon
2. Click "Scan All Links" under "Current Page"
3. See statistics for the current page

### Understanding Visual Indicators

#### 🛑 Danger (Red Background)
- **Meaning**: High-confidence phishing detection
- **Action**: DO NOT click! Link is very likely malicious
- **Visual**: Red background, strikethrough text, pulsing warning icon
- **Click Behavior**: Shows confirmation dialog with risk details

#### ⚠️ Warning (Yellow Background)
- **Meaning**: Suspicious link, potential phishing
- **Action**: Proceed with caution
- **Visual**: Yellow background, warning icon
- **Click Behavior**: Normal click, but stay alert

#### ✓ Safe (Green Checkmark)
- **Meaning**: Verified safe link
- **Action**: Safe to click
- **Visual**: Small green checkmark (subtle)
- **Click Behavior**: Normal

## 🔧 Troubleshooting

### Extension Not Working

**Problem**: Links aren't being scanned
- **Check**: Extension is enabled (`chrome://extensions/`)
- **Check**: API URL is correct in settings
- **Check**: TrustLink backend is running
- **Check**: Test connection in settings page

**Problem**: "Connection failed" error
- **Solution**: Make sure TrustLink backend is running on the correct port
- **Solution**: Try accessing `http://localhost:5000/health` in your browser
- **Solution**: Check firewall settings

### Performance Issues

**Problem**: Page loading is slow
- **Solution**: Increase scan delay in settings (e.g., 1000ms)
- **Solution**: Disable auto-scan on page load
- **Solution**: Reduce cache duration for fewer stored results

**Problem**: Too many false warnings
- **Solution**: Increase confidence threshold (e.g., 70%)
- **Solution**: Disable real-time scanning for specific sites

### Visual Issues

**Problem**: Indicators don't show up
- **Solution**: Refresh the page after changing settings
- **Solution**: Check that "Real-Time Scanning" is enabled
- **Solution**: Some websites may override styles (rare)

**Problem**: Tooltips are cut off
- **Solution**: This is a CSS limitation on some sites
- **Solution**: Click the TrustLink icon for detailed results

## 🔐 Privacy & Security

### Data Collection
- **Links Scanned**: URLs are sent to your configured TrustLink API
- **No Tracking**: Extension does not track your browsing
- **Local Cache**: Scan results stored locally in browser

### API Communication
- **Your Server**: Extension connects to YOUR TrustLink instance
- **Self-Hosted**: You control where data is sent
- **API Keys**: Optional authentication for your API

### Permissions
- **Storage**: Store settings and cache
- **ActiveTab**: Access current tab for scanning
- **Host Permissions**: Scan links on all websites

## 🎯 Best Practices

### For Maximum Protection
1. Keep real-time scanning enabled
2. Set confidence threshold to 50% or lower
3. Enable auto-scan on page load
4. Always read warning dialogs before clicking through

### For Performance
1. Use caching (24-hour duration)
2. Set scan delay to 500-1000ms
3. Disable safe indicators if not needed
4. Consider selective scanning for trusted sites

### For Teams
1. Use API keys for user tracking
2. Set up central TrustLink server
3. Configure same settings across team
4. Monitor analytics in dashboard

## 🔄 Updates & Maintenance

### Clearing Cache
- Go to Settings → Cache Settings → "Clear Cache Now"
- Recommended: Clear cache weekly or after ML model updates

### Updating Extension
1. Download latest version
2. Remove old extension
3. Load new version (unpacked)
4. Settings are preserved in browser storage

## 🐛 Known Issues

1. **Some sites block external scripts**: Extension may not work on browser internal pages (chrome://, about:, etc.)
2. **Dynamic content**: Very fast-loading content may not be scanned immediately
3. **Styling conflicts**: Some websites may override indicator styles

## 📞 Support

### Getting Help
- **Documentation**: See main TrustLink README.md
- **API Guide**: See API_GUIDE.md
- **Issues**: Report bugs on GitHub

### Contributing
Contributions welcome! Areas for improvement:
- Support for more browsers (Safari, Opera)
- Offline mode with local ML model
- Whitelist management in extension
- Custom styling themes
- Import/export settings

## 📄 License

This extension is part of the TrustLink project. See main LICENSE file.

## 🎉 Enjoy Safe Browsing!

TrustLink protects you from phishing attacks in real-time. Browse with confidence! 🛡️

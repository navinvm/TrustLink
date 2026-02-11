# 📦 TrustLink Extension Installation Guide

Step-by-step instructions for installing the TrustLink browser extension.

## Prerequisites

Before installing the extension, make sure you have:

1. ✅ **TrustLink Backend Running**
   ```bash
   cd /path/to/trustlink
   python app.py
   ```
   Server should be accessible at `http://localhost:5000`

2. ✅ **Supported Browser**
   - Google Chrome (version 88+)
   - Microsoft Edge (version 88+)
   - Brave Browser
   - Firefox (version 109+)
   - Any Chromium-based browser

3. ✅ **Extension Files**
   - Download or clone the repository
   - Locate the `browser-extension` folder

## Installation Steps

### 🟦 Chrome / Edge / Brave (Chromium-based browsers)

#### Step 1: Open Extensions Page

**Chrome:**
- Navigate to `chrome://extensions/`
- Or click the three-dot menu → More Tools → Extensions

**Edge:**
- Navigate to `edge://extensions/`
- Or click the three-dot menu → Extensions

**Brave:**
- Navigate to `brave://extensions/`
- Or click the menu → Extensions

#### Step 2: Enable Developer Mode

1. Look for a toggle switch labeled "Developer mode" (usually top-right)
2. Turn it ON
3. New buttons will appear: "Load unpacked", "Pack extension", "Update"

#### Step 3: Load Extension

1. Click the **"Load unpacked"** button
2. A file browser will open
3. Navigate to and select the `browser-extension` folder
4. Click "Select Folder" (Windows) or "Open" (Mac)

#### Step 4: Verify Installation

You should see:
- ✅ TrustLink card appears in your extensions list
- ✅ TrustLink icon appears in your browser toolbar
- ✅ Status shows "Enabled"

If the icon isn't visible in toolbar:
- Click the puzzle piece icon (Extensions) in toolbar
- Find TrustLink in the list
- Click the pin icon to keep it visible

#### Step 5: Configure Extension

1. Click the TrustLink icon in your toolbar
2. Click **"⚙️ Settings"** button
3. Enter your API URL: `http://localhost:5000`
4. Click **"🔍 Test Connection"** to verify
5. If successful, click **"💾 Save Settings"**

### 🟧 Firefox

#### Step 1: Open Debugging Page

1. Type `about:debugging` in the address bar
2. Press Enter
3. Click **"This Firefox"** in the left sidebar

#### Step 2: Load Temporary Extension

1. Click **"Load Temporary Add-on..."**
2. Navigate to the `browser-extension` folder
3. Select the **`manifest.json`** file
4. Click "Open"

#### Step 3: Verify Installation

You should see:
- ✅ TrustLink listed under "Temporary Extensions"
- ✅ TrustLink icon in toolbar
- ✅ Status shows details and controls

**⚠️ Note**: Temporary extensions are removed when Firefox restarts. You'll need to reload it each time.

#### Step 4: Configure Extension

1. Click the TrustLink icon
2. Go to Settings
3. Enter API URL and configure preferences
4. Save settings

#### For Permanent Installation (Advanced)

Firefox requires extensions to be signed by Mozilla:
1. Package the extension as a .zip file
2. Submit to [addons.mozilla.org](https://addons.mozilla.org/developers/)
3. Wait for review and signing
4. Install signed .xpi file

## First-Time Setup

### 1. Test Backend Connection

Before using the extension, verify your backend is working:

```bash
# Test from command line
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","model_loaded":true,...}
```

Or open in browser: `http://localhost:5000/health`

### 2. Configure Extension Settings

Click the TrustLink icon → Settings (⚙️):

**Connection Settings:**
- API URL: `http://localhost:5000` (or your server URL)
- API Key: (optional) Get from dashboard

**Scanning Settings:**
- ☑️ Enable Real-Time Scanning
- ☑️ Auto-Scan on Page Load
- Scan Delay: 500ms (recommended)
- Confidence Threshold: 50% (recommended)

**Display Settings:**
- ☑️ Show Safe Indicators (optional)

**Cache Settings:**
- ☑️ Enable Caching
- Cache Duration: 24 Hours (recommended)

Click **"💾 Save Settings"**

### 3. Test the Extension

1. Visit a test page with links (e.g., Google.com)
2. Open the popup (click TrustLink icon)
3. Click **"Scan All Links"** under "Current Page"
4. Links should be highlighted with indicators

### 4. Quick Scan Test

1. Click TrustLink icon
2. Enter a URL in "Quick Scan": `https://google.com`
3. Click "Scan URL"
4. Should show "✅ Safe" result

## Common Installation Issues

### Issue: "Cannot read manifest.json"

**Cause**: Wrong folder selected

**Solution**: 
- Make sure you select the `browser-extension` folder itself
- The folder should contain `manifest.json` at the root level
- Don't select a parent folder or a subfolder

### Issue: "Extension failed to load"

**Cause**: Missing files or corrupted download

**Solution**:
- Re-download the extension files
- Verify all files are present (manifest.json, background.js, content.js, etc.)
- Check for file permission issues

### Issue: Extension icon not visible

**Cause**: Icon not pinned to toolbar

**Solution**:
- Click the puzzle piece icon (Extensions) in toolbar
- Find TrustLink
- Click the pin icon next to it

### Issue: "Connection failed" in settings

**Cause**: Backend not running or wrong URL

**Solutions**:
1. Start the backend: `python app.py`
2. Verify backend is running: Open `http://localhost:5000` in browser
3. Check firewall isn't blocking port 5000
4. Try `http://127.0.0.1:5000` instead
5. Check API URL doesn't have trailing slash

### Issue: Extension not scanning links

**Causes & Solutions**:

1. **Real-time scanning disabled**
   - Settings → Enable Real-Time Scanning → Save

2. **Wrong API URL**
   - Settings → Check API URL → Test Connection

3. **Backend not responding**
   - Restart backend server
   - Check server logs for errors

4. **Page loaded before extension**
   - Refresh the page
   - Or click "Scan All Links" manually

### Issue: Firefox extension disappears after restart

**Cause**: Temporary extensions are removed on restart

**Solutions**:
- Reload extension each time you start Firefox
- Or, package and sign for permanent installation
- Or, use Firefox Developer Edition with different settings

## Production Deployment

For deploying to a team or making public:

### Chrome Web Store (Public Release)

1. Create a [Chrome Web Store Developer account](https://chrome.google.com/webstore/devconsole/) ($5 one-time fee)
2. Package your extension:
   ```bash
   zip -r trustlink-extension.zip browser-extension/
   ```
3. Upload to Chrome Web Store
4. Fill out listing details
5. Submit for review (usually 1-3 days)

### Firefox Add-ons (Public Release)

1. Create account on [addons.mozilla.org](https://addons.mozilla.org/developers/)
2. Package extension as .zip
3. Submit for signing and review
4. Wait for approval

### Enterprise Deployment (Internal Use)

**Chrome/Edge:**
- Use Group Policy to deploy extensions
- Or distribute as .crx file with enterprise policy

**Firefox:**
- Use Firefox Enterprise Policy
- Or distribute signed .xpi file

## Updating the Extension

### Development Version (Unpacked)

1. Download new version files
2. Replace files in `browser-extension` folder
3. Go to extensions page
4. Click "Reload" button (🔄) for TrustLink

### Store Version

1. Update happens automatically
2. Or click "Update" in extensions page

## Uninstalling

### Chrome/Edge/Brave

1. Go to extensions page
2. Find TrustLink
3. Click "Remove"
4. Confirm removal

### Firefox

1. Go to `about:addons`
2. Find TrustLink
3. Click "..." menu
4. Select "Remove"

**Note**: Settings and cache are removed with the extension.

## Next Steps

After installation:
1. ✅ Read the [README.md](README.md) for usage guide
2. ✅ Test on various websites
3. ✅ Customize settings to your preference
4. ✅ Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues arise

## Getting Help

- **Check**: Main TrustLink documentation
- **Check**: Extension README.md
- **Report**: Issues on GitHub
- **Ask**: Questions in discussions

---

**Happy browsing! Stay safe with TrustLink! 🛡️**

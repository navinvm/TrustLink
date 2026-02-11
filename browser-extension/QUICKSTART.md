# ⚡ TrustLink Extension - 5-Minute Quick Start

Get phishing protection in your browser in just 5 minutes!

## Step 1: Start TrustLink Backend (1 minute)

```bash
# Navigate to TrustLink directory
cd /path/to/trustlink

# Start the server
python app.py

# You should see:
# ✓ Model and vectorizer loaded successfully
# * Running on http://127.0.0.1:5000
```

Keep this terminal window open!

## Step 2: Install Extension (2 minutes)

### Chrome / Edge / Brave

1. Open `chrome://extensions/` in your browser
2. Toggle **"Developer mode"** ON (top-right corner)
3. Click **"Load unpacked"**
4. Select the `browser-extension` folder
5. Done! Look for the TrustLink icon in your toolbar

### Firefox

1. Open `about:debugging#/runtime/this-firefox`
2. Click **"Load Temporary Add-on"**
3. Select `browser-extension/manifest.json`
4. Done! Look for the TrustLink icon in your toolbar

## Step 3: Configure Extension (1 minute)

1. Click the **TrustLink icon** in your toolbar
2. Click **"⚙️ Settings"** button
3. Enter: `http://localhost:5000` in API URL field
4. Click **"🔍 Test Connection"** → Should show ✅ Success
5. Click **"💾 Save Settings"**

## Step 4: Test It Out (1 minute)

### Test Automatic Scanning

1. Visit **https://www.google.com**
2. Links should automatically be marked with ✓ safe indicators
3. Check the TrustLink icon - badge shows scan count

### Test Manual Scan

1. Click the **TrustLink icon**
2. In "Quick Scan" field, enter: `https://github.com`
3. Click **"Scan URL"**
4. Should show ✅ Safe result with confidence score

### Test Warning System

1. Try scanning a suspicious URL (if you have one)
2. Or visit the TrustLink dashboard at `http://localhost:5000`
3. Check scan history and analytics

## 🎉 You're Protected!

The extension is now:
- ✅ Scanning all links automatically
- ✅ Showing visual warnings for threats
- ✅ Protecting you from phishing attacks

## Next Steps

- 📖 Read [README.md](README.md) for full feature list
- ⚙️ Customize settings to your preference
- 🔐 Get an API key from the dashboard for advanced features
- 📊 View scan history and analytics

## Quick Tips

### For Maximum Protection
- Keep real-time scanning enabled
- Set confidence threshold to 50% or lower
- Enable auto-scan on page load

### If Something's Wrong
- Check backend is running (terminal should show no errors)
- Test connection in settings
- Refresh the webpage
- Check browser console (F12) for errors

## Common URLs to Test

Safe URLs (should show ✅):
- `https://google.com`
- `https://github.com`
- `https://microsoft.com`
- `https://wikipedia.org`

The extension uses TrustLink's ML model and whitelist to detect threats!

---

**Need help?** Check [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

**Browse safely! 🛡️**

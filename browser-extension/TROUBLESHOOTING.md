# 🔧 TrustLink Extension - Troubleshooting Guide

## Issue: Extension Won't Load in Browser

### For Chrome / Edge / Brave

#### Method 1: Load Unpacked (Recommended)

**Step-by-Step:**

1. **Open Extensions Page**
   - Chrome: Type `chrome://extensions/` in address bar and press Enter
   - Edge: Type `edge://extensions/` in address bar and press Enter
   - Brave: Type `brave://extensions/` in address bar and press Enter

2. **Enable Developer Mode**
   - Look for a toggle switch labeled "Developer mode" in the TOP-RIGHT corner
   - Click it to turn it ON (should turn blue/colored)
   - You should now see new buttons: "Load unpacked", "Pack extension", "Update"

3. **Load the Extension**
   - Click the **"Load unpacked"** button (top-left area)
   - A file browser window will open
   - Navigate to: `C:\Users\ACIL\Desktop\portfolio.vs\CAPSTONE\TechStack\browser-extension`
   - Make sure you select the `browser-extension` FOLDER itself (not a file inside it)
   - Click "Select Folder" (Windows) or "Open" (Mac)

4. **Verify Installation**
   - You should see a card appear with:
     - Icon with "TL" text
     - Name: "TrustLink - Phishing Protection"
     - Version: 1.0.0
     - Status: Enabled (toggle should be ON)
   - Look for the TrustLink icon in your browser toolbar (may need to click puzzle piece icon to pin it)

#### Common Chrome/Edge Errors:

**Error: "Manifest file is missing or unreadable"**
- **Cause**: Wrong folder selected
- **Solution**: Make sure you select `browser-extension` folder, not its parent folder
- **Check**: The folder should contain `manifest.json` at the root level

**Error: "Failed to load extension"**
- **Cause**: Permission issues or corrupted files
- **Solution**: 
  1. Close browser completely
  2. Restart browser as Administrator (right-click → Run as administrator)
  3. Try loading again

**Error: Icons not showing**
- **Cause**: Icon files missing or wrong path
- **Solution**: Verify icons exist in `browser-extension/icons/` folder

**Extension loads but no icon in toolbar**
- **Cause**: Icon not pinned
- **Solution**:
  1. Click the puzzle piece icon (Extensions) in your toolbar
  2. Find "TrustLink - Phishing Protection" in the list
  3. Click the pin icon (📌) next to it

---

### For Firefox

#### Method: Load Temporary Extension

**Step-by-Step:**

1. **Open Debugging Page**
   - Type `about:debugging` in the address bar
   - Press Enter
   - You'll see a page with several tabs on the left

2. **Select "This Firefox"**
   - Click on "This Firefox" in the left sidebar
   - You'll see options for temporary extensions

3. **Load Extension**
   - Click the **"Load Temporary Add-on..."** button
   - A file browser will open
   - Navigate to: `C:\Users\ACIL\Desktop\portfolio.vs\CAPSTONE\TechStack\browser-extension`
   - Select the `manifest.json` FILE (not the folder)
   - Click "Open"

4. **Verify Installation**
   - Extension should appear under "Temporary Extensions"
   - You should see the TrustLink icon in your toolbar

#### Firefox Notes:
- ⚠️ Temporary extensions are removed when Firefox closes
- You need to reload the extension each time you restart Firefox
- For permanent installation, the extension needs to be signed by Mozilla

#### Common Firefox Errors:

**Error: "There was an error during installation"**
- **Cause**: Manifest not compatible
- **Solution**: Firefox may have stricter requirements - check console for details

**Extension disappears after restart**
- **Cause**: This is normal for temporary extensions
- **Solution**: Reload the extension each time, or package and sign it

---

## Step-by-Step Video Guide

### Chrome Installation (Visual Guide)

```
1. Open new tab
   ↓
2. Type: chrome://extensions
   ↓
3. Top-right corner → Toggle "Developer mode" ON
   ↓
4. Top-left → Click "Load unpacked"
   ↓
5. Select folder: .../TechStack/browser-extension
   ↓
6. Click "Select Folder"
   ↓
7. Extension appears in list
   ↓
8. Look for icon in toolbar (may need to pin it)
```

---

## Alternative: Try This Quick Fix

If you're having trouble, try this PowerShell command to open the extensions page:

**For Chrome:**
```powershell
Start-Process "chrome://extensions/"
```

**For Edge:**
```powershell
Start-Process "microsoft-edge://extensions/"
```

**For Firefox:**
```powershell
Start-Process "about:debugging#/runtime/this-firefox"
```

---

## Verification Checklist

After loading, verify these:

- [ ] Extension appears in extensions list
- [ ] Name shows: "TrustLink - Phishing Protection"
- [ ] Version shows: 1.0.0
- [ ] Status shows: Enabled (toggle is ON)
- [ ] Icon appears in toolbar (or available in puzzle piece menu)
- [ ] No error messages displayed
- [ ] Clicking icon opens popup

---

## Still Not Working?

### Check Browser Console for Errors

1. Go to `chrome://extensions/` (or equivalent)
2. Find TrustLink extension
3. Click "Details" button
4. Click "Inspect views: service worker" (for background)
5. Check Console tab for error messages

### Common Console Errors:

**"Failed to load resource: net::ERR_FILE_NOT_FOUND"**
- Missing file - check which file is mentioned
- Verify file exists in browser-extension folder

**"Uncaught SyntaxError"**
- JavaScript error in one of the files
- Check the file mentioned in the error

**"Extension manifest must request permission"**
- Permissions issue - should be fine with current manifest

---

## Manual Installation Checklist

Verify each step:

1. [ ] Browser is Chrome/Edge/Brave (version 88+) or Firefox (109+)
2. [ ] Developer mode is enabled (Chrome/Edge/Brave only)
3. [ ] Selected correct folder: `browser-extension`
4. [ ] Folder contains `manifest.json` at root level
5. [ ] All icon files exist in `icons/` subfolder
6. [ ] No antivirus blocking the files
7. [ ] Browser has permission to access the folder

---

## Try These If Nothing Works

### 1. Restart Browser
```
1. Close browser completely (check Task Manager to ensure closed)
2. Reopen browser
3. Try loading extension again
```

### 2. Use Different Browser
```
- If Chrome doesn't work, try Edge
- If Edge doesn't work, try Brave
- Firefox uses different method (see above)
```

### 3. Check File Permissions
```powershell
# Run in PowerShell (as Administrator)
$path = "C:\Users\ACIL\Desktop\portfolio.vs\CAPSTONE\TechStack\browser-extension"
icacls $path /grant Everyone:F /T
```

### 4. Create New Clean Folder
```powershell
# Copy to a simpler path
Copy-Item "browser-extension" "C:\TrustLink-Extension" -Recurse
# Then try loading from C:\TrustLink-Extension
```

### 5. Check Antivirus
- Some antivirus software blocks loading unpacked extensions
- Temporarily disable antivirus and try again
- Add browser-extension folder to antivirus whitelist

---

## Test Extension After Loading

Once loaded successfully:

1. **Test Popup**
   - Click the TrustLink icon in toolbar
   - Popup should open showing stats and quick scan

2. **Test Settings**
   - Click icon → Click ⚙️ Settings
   - Settings page should open in new tab

3. **Test Console**
   - Press F12 on any webpage
   - Go to Console tab
   - You should see: `[TrustLink] Content script loaded`

---

## Get Help

If still having issues, gather this info:

1. **Browser & Version**: (e.g., Chrome 120.0.6099.109)
   - Check: Settings → About Chrome

2. **Error Messages**: Any red errors in:
   - Extensions page
   - Browser console (F12)
   - Background service worker console

3. **Screenshot**: Take screenshot of extensions page showing the issue

4. **What You Tried**: List steps you followed

---

## Quick Test Script

Run this to verify all files:

```powershell
cd "C:\Users\ACIL\Desktop\portfolio.vs\CAPSTONE\TechStack"

Write-Host "Testing extension files..." -ForegroundColor Cyan

# Check manifest
if (Test-Path "browser-extension\manifest.json") {
    Write-Host "✓ manifest.json found" -ForegroundColor Green
    $manifest = Get-Content "browser-extension\manifest.json" | ConvertFrom-Json
    Write-Host "  Name: $($manifest.name)" -ForegroundColor Gray
} else {
    Write-Host "✗ manifest.json MISSING" -ForegroundColor Red
}

# Check key files
$files = @("background.js", "content.js", "popup.html", "options.html")
foreach ($file in $files) {
    if (Test-Path "browser-extension\$file") {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file MISSING" -ForegroundColor Red
    }
}

# Check icons
$icons = @("icon16.png", "icon32.png", "icon48.png", "icon128.png")
foreach ($icon in $icons) {
    if (Test-Path "browser-extension\icons\$icon") {
        Write-Host "✓ icons/$icon" -ForegroundColor Green
    } else {
        Write-Host "✗ icons/$icon MISSING" -ForegroundColor Red
    }
}

Write-Host "`nFull path to load:" -ForegroundColor Cyan
Write-Host (Get-Item "browser-extension").FullName -ForegroundColor Yellow
```

---

## Success Criteria

Extension is working when you see:

✅ Extension card appears in extensions list  
✅ Toggle is ON (enabled)  
✅ Icon visible in toolbar  
✅ Clicking icon opens popup  
✅ Popup shows "Protected" status  
✅ Settings page opens from popup  
✅ No error messages  

---

**Need more help? Let me know what error message you're seeing!**

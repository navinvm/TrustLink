# 📧 Quick Email Setup Guide - Fix Email Verification

## Problem
Email verification not sending because `.env` has placeholder values:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password-here
```

---

## ✅ Solution: Setup Gmail App Password (5 minutes)

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to your Google Account: https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the setup (you'll need your phone)
4. Enable 2FA

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. If you don't see "App passwords", make sure 2FA is enabled
3. Select app: **Mail**
4. Select device: **Windows Computer** (or Other)
5. Click **Generate**
6. Copy the 16-character password (example: `abcd efgh ijkl mnop`)

### Step 3: Update .env File
Open `.env` and replace:

```env
SENDER_EMAIL=your-actual-email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop
ADMIN_EMAIL=your-actual-email@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

**Example:**
```env
SENDER_EMAIL=john.doe@gmail.com
SENDER_PASSWORD=xyzw abcd efgh ijkl
ADMIN_EMAIL=john.doe@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

### Step 4: Restart Your App
```powershell
# Stop current app (Ctrl+C)
# Start again
python app.py
```

### Step 5: Test!
1. Go to: http://localhost:5000/register
2. Register with a real email address
3. Check your inbox for verification email
4. Click the link to verify

---

## 🔧 Alternative: Use Different Email Provider

### Option 1: Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=yourname@outlook.com
SENDER_PASSWORD=your-outlook-password
```

### Option 2: Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=yourname@yahoo.com
SENDER_PASSWORD=your-yahoo-app-password
```

### Option 3: Custom SMTP
```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-password
```

---

## 🧪 Test Email Configuration

Run this test script:

```powershell
python -c "from email_notifier import EmailNotifier; import os; from dotenv import load_dotenv; load_dotenv(); notifier = EmailNotifier(); print('Configured:', notifier.is_configured()); print('Sender:', notifier.sender_email)"
```

Should output:
```
Configured: True
Sender: your-email@gmail.com
```

---

## ❌ Troubleshooting

### Error: "Username and Password not accepted"
**Fix:** Make sure you're using an App Password, not your regular Gmail password

### Error: "SMTPAuthenticationError"
**Fix:** 
1. Enable "Less secure app access" (not recommended)
2. OR use App Password (recommended)

### Emails not arriving
**Fix:**
1. Check spam folder
2. Verify SMTP settings are correct
3. Check Gmail "Sent" folder to confirm email was sent

### Error: "Email not configured"
**Fix:** Check all values in `.env`:
```powershell
# Verify env variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('SENDER_EMAIL:', os.getenv('SENDER_EMAIL')); print('ENABLED:', os.getenv('EMAIL_NOTIFICATIONS_ENABLED'))"
```

---

## 🚀 Quick Fix (Copy-Paste)

1. Get your Gmail App Password: https://myaccount.google.com/apppasswords

2. Update `.env` (replace with YOUR values):
```env
SENDER_EMAIL=yourname@gmail.com
SENDER_PASSWORD=your-16-char-app-password
ADMIN_EMAIL=yourname@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

3. Restart app:
```powershell
python app.py
```

4. Test registration at: http://localhost:5000/register

---

## ✅ Success!

When configured correctly, you'll see on app startup:
```
✓ Email notifications enabled
```

Instead of:
```
⚠ Email notifications not configured (set environment variables)
```

---

**Still having issues?** 
- Make sure you're using Gmail App Password, not regular password
- Check that 2FA is enabled on your Google account
- Verify no typos in email address
- Make sure `.env` file is in the same directory as `app.py`

# 🚀 TrustLink v2.1 - Quick Start Guide

## What's New?

TrustLink v2.1 includes three major improvements:

1. ✅ **Email Verification** - Users must verify their email before logging in
2. 🔑 **Password Reset** - Forgot password functionality via email
3. 🎨 **Enhanced Extension** - Modern UI with smooth animations and better UX

---

## 📧 Email Configuration (Required for Email Features)

### Option 1: Using Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Google Account
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "TrustLink"
   - Copy the 16-character password

3. **Create `.env` file** in the project root:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   ADMIN_EMAIL=your-email@gmail.com
   EMAIL_NOTIFICATIONS_ENABLED=true
   ```

### Option 2: Using Other Email Providers

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
ADMIN_EMAIL=your-email@outlook.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

#### Custom SMTP Server
```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-password
ADMIN_EMAIL=admin@yourdomain.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

### Option 3: Development Mode (No Email)

For testing without email configuration, the system will work but show messages like:
- "Email verification is disabled in development mode"
- Emails won't actually be sent

---

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements-scalability.txt
```

This installs all required packages including email support.

### 2. Database Migration

The database will automatically update on first run. If you have existing users, you may want to verify them manually:

```python
# Optional: Mark existing users as verified
python -c "
import sqlite3
conn = sqlite3.connect('trustlink.db')
conn.execute('UPDATE users SET email_verified = 1 WHERE created_at < datetime(\"now\")')
conn.commit()
print('Existing users marked as verified')
"
```

### 3. Start the Application

```bash
python app.py
```

You should see:
```
✓ Model and vectorizer loaded successfully
✓ Advanced feature extraction enabled
✓ Loaded existing model for retraining
✓ Learning system enabled
✓ Email notifications enabled  <-- This confirms email is working
⚠ Email notifications not configured  <-- If you see this, check .env
```

---

## 👤 Testing the New Features

### Test Email Verification

1. **Register a New User**
   - Go to http://localhost:5000/register
   - Fill in username, email, password
   - Click "Create Account"

2. **Check Your Email**
   - You should receive a verification email
   - Click the verification link
   - You'll be redirected to login

3. **Try to Login Before Verification**
   - Enter credentials
   - You'll see: "Please verify your email before logging in"
   - Click "Resend Verification Email" if needed

### Test Password Reset

1. **Go to Login Page**
   - Click "Forgot your password?"

2. **Enter Your Email**
   - Enter registered email address
   - Click "Send Reset Link"

3. **Check Your Email**
   - You'll receive a password reset email
   - Click the reset link (valid for 1 hour)

4. **Reset Your Password**
   - Enter new password (twice)
   - Must meet requirements:
     - Minimum 8 characters
     - Uppercase letter
     - Lowercase letter
     - Number
     - Special character

5. **Login with New Password**
   - Use your new password to log in

### Test Enhanced Extension

1. **Load Extension in Browser**
   - Chrome: Go to `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `browser-extension` folder

2. **Try New Features**
   - Click extension icon to open popup
   - Notice smooth animations and modern design
   - Try keyboard shortcuts:
     - `Ctrl+K` to focus URL input
     - `Enter` to scan
     - `Esc` to clear results
   - Click on domains to copy them
   - Toggle Safe Mode and see the status message
   - Hover over elements to see tooltips

---

## 🎯 Usage Examples

### Email Verification Flow

```
User Registration → Email Sent → User Clicks Link → Email Verified → Login Allowed
     ↓
Without Email Configured: Success message shown but no email sent
```

### Password Reset Flow

```
Forgot Password → Enter Email → Email Sent → Click Link → Enter New Password → Login
     ↓
Token expires in 1 hour
One-time use only
```

### Extension Features

```
Modern UI → Smooth Animations → Keyboard Shortcuts → Copy to Clipboard
     ↓                ↓                 ↓                    ↓
Glassmorphism   Fade/Slide      Ctrl+K Focus        Click Domain
Design          Effects         Enter Scan          to Copy
```

---

## 🔍 Troubleshooting

### Email Not Sending?

1. **Check .env file exists and has correct values**
   ```bash
   cat .env  # Linux/Mac
   type .env  # Windows
   ```

2. **Check Flask startup logs**
   - Look for "✓ Email notifications enabled"
   - If you see "⚠ Email notifications not configured", check your .env

3. **Gmail App Password Issues**
   - Make sure you used App Password, not regular password
   - App password should be 16 characters without spaces
   - 2FA must be enabled on Google account

4. **Test Email Manually**
   ```python
   from email_notifier import EmailNotifier
   
   notifier = EmailNotifier({
       'smtp_server': 'smtp.gmail.com',
       'smtp_port': 587,
       'sender_email': 'your-email@gmail.com',
       'sender_password': 'your-app-password',
       'admin_email': 'your-email@gmail.com',
       'enabled': True
   })
   
   if notifier.is_configured():
       print("✓ Email configured correctly")
       notifier.send_verification_email(
           'test@example.com',
           'TestUser',
           'test_token_123',
           'http://localhost:5000'
       )
   else:
       print("✗ Email not configured")
   ```

### Database Issues?

**Reset Database (CAUTION: Deletes all data)**
```bash
# Backup first
cp trustlink.db trustlink.db.backup

# Delete and restart (will recreate automatically)
rm trustlink.db
python app.py
```

**Check Database Schema**
```bash
sqlite3 trustlink.db ".schema users"
```

Should show:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    email_verified BOOLEAN DEFAULT 0,  <-- New
    verification_token TEXT,            <-- New
    verification_token_expires TIMESTAMP <-- New
);
```

### Extension Not Working?

1. **Reload Extension**
   - Go to `chrome://extensions`
   - Click reload button on TrustLink

2. **Check Console for Errors**
   - Right-click extension popup
   - Click "Inspect"
   - Look for errors in Console tab

3. **Clear Extension Storage**
   ```javascript
   // In extension console
   chrome.storage.local.clear(() => console.log('Cleared'));
   ```

---

## 📊 Configuration Options

### Email Settings (Environment Variables)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SMTP_SERVER` | SMTP server address | smtp.gmail.com | No |
| `SMTP_PORT` | SMTP server port | 587 | No |
| `SENDER_EMAIL` | Email address to send from | - | Yes* |
| `SENDER_PASSWORD` | Email password or app password | - | Yes* |
| `ADMIN_EMAIL` | Admin email for notifications | - | Yes* |
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable/disable emails | false | No |

*Required only if you want email features to work

### Security Settings

| Setting | Description | Value |
|---------|-------------|-------|
| Verification Token Expiry | Email verification link | 24 hours |
| Password Reset Token Expiry | Password reset link | 1 hour |
| Token Format | Secure random string | URL-safe base64 |
| Password Requirements | Minimum strength | 8+ chars, upper, lower, digit, special |

---

## 🎨 Extension Customization

### Keyboard Shortcuts

You can modify shortcuts in `browser-extension/popup-enhanced.js`:

```javascript
// Line ~195
document.addEventListener('keydown', function(e) {
  // Ctrl/Cmd + K to focus URL input
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    // Your custom shortcut
  }
});
```

### Theme Colors

Modify colors in `browser-extension/popup-enhanced.css`:

```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Accent color */
color: #00D2FF;
```

---

## 📈 Monitoring

### Check Email Statistics

```python
# In Python console
from database import Database
db = Database()

# Get users needing verification
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE email_verified = 0')
    print(f"Unverified users: {cursor.fetchone()[0]}")
```

### Check Password Reset Tokens

```python
# Check active reset tokens
cursor.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE used = 0 AND expires_at > datetime("now")')
print(f"Active reset tokens: {cursor.fetchone()[0]}")
```

---

## 🚀 Production Deployment

### Before Deploying

1. **Use a proper SMTP service** (SendGrid, Mailgun, AWS SES)
2. **Set strong SECRET_KEY** in app.py
3. **Enable HTTPS** for all routes
4. **Set secure cookie settings**
5. **Configure proper domain** in email links
6. **Test all email flows** in staging

### Environment Variables for Production

```env
# Email
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-sendgrid-api-key
ADMIN_EMAIL=admin@yourdomain.com
EMAIL_NOTIFICATIONS_ENABLED=true

# Security
SECRET_KEY=your-long-random-secret-key
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict

# Application
FLASK_ENV=production
BASE_URL=https://trustlink.yourdomain.com
```

---

## 💡 Tips & Best Practices

### For Users
- ✅ Verify your email immediately after registration
- ✅ Use a strong, unique password
- ✅ Keep your email address up to date
- ✅ Enable Safe Mode in browser extension

### For Developers
- ✅ Never commit `.env` file to version control
- ✅ Use app passwords for Gmail, not account password
- ✅ Test email in development before deploying
- ✅ Monitor email delivery rates in production
- ✅ Set up email sending limits to prevent abuse
- ✅ Log all email send attempts for debugging

---

## 📞 Need Help?

- 📖 **Detailed Docs**: See `IMPROVEMENTS_SUMMARY_v2.md`
- 🎨 **Extension Guide**: See `browser-extension/EXTENSION_IMPROVEMENTS.md`
- 🐛 **Issues**: Check console logs and error messages
- 💬 **Support**: [Your support channel]

---

## ✅ Checklist

Before using in production:

- [ ] Email configuration tested and working
- [ ] All environment variables set correctly
- [ ] Database backup strategy in place
- [ ] HTTPS enabled for production
- [ ] Email templates customized with your branding
- [ ] Password reset flow tested
- [ ] Email verification flow tested
- [ ] Browser extension loaded and tested
- [ ] Monitoring and logging configured
- [ ] Rate limiting enabled for email sends

---

🎉 **You're all set! Enjoy the new features of TrustLink v2.1!**

For detailed information, see `IMPROVEMENTS_SUMMARY_v2.md`

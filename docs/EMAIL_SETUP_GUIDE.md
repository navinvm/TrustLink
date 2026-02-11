# 📧 Email Notification Setup Guide

## Overview
TrustLink can now send email notifications when:
- Users submit feedback (corrections to predictions)
- Model is retrained with new data

Admins receive beautifully formatted HTML emails with all relevant information.

---

## 🚀 Quick Setup (5 Minutes)

### Option 1: Gmail (Easiest - FREE)

#### Step 1: Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the setup wizard

#### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Click "Generate"
4. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

#### Step 3: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "abcdefghijklmnop"  # Remove spaces from app password
$env:ADMIN_EMAIL = "admin@example.com"
$env:EMAIL_NOTIFICATIONS_ENABLED = "true"
```

**Linux/Mac:**
```bash
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="abcdefghijklmnop"
export ADMIN_EMAIL="admin@example.com"
export EMAIL_NOTIFICATIONS_ENABLED="true"
```

#### Step 4: Restart TrustLink
```bash
python app.py
```

You should see:
```
✓ Email notifications enabled
```

---

### Option 2: Outlook/Office 365

#### Environment Variables:
```powershell
$env:SMTP_SERVER = "smtp.office365.com"
$env:SMTP_PORT = "587"
$env:SENDER_EMAIL = "your-email@outlook.com"
$env:SENDER_PASSWORD = "your-password"
$env:ADMIN_EMAIL = "admin@example.com"
$env:EMAIL_NOTIFICATIONS_ENABLED = "true"
```

---

### Option 3: Custom SMTP Server

```powershell
$env:SMTP_SERVER = "mail.yourdomain.com"
$env:SMTP_PORT = "587"
$env:SENDER_EMAIL = "noreply@yourdomain.com"
$env:SENDER_PASSWORD = "your-smtp-password"
$env:ADMIN_EMAIL = "admin@yourdomain.com"
$env:EMAIL_NOTIFICATIONS_ENABLED = "true"
```

---

## 📨 Email Notifications

### 1. Feedback Notification
**Sent when:** User reports incorrect prediction

**Includes:**
- 🌐 URL that was scanned
- 📊 Original prediction vs user correction
- 👤 Username (or "Anonymous")
- ⏰ Timestamp
- 🔗 Link to dashboard

**Example:**
```
⚠️ TrustLink: INCORRECT PREDICTION - User Feedback

URL: http://phishing-site.com
Original Prediction: Safe
User Says: Phishing
Submitted By: john_doe
Timestamp: 2026-02-05 14:30:00
```

### 2. Retrain Notification
**Sent when:** Model is successfully retrained

**Includes:**
- 🆕 New model version
- 📈 Performance metrics (accuracy, precision, recall)
- 📚 Number of training samples
- ⏰ Timestamp

**Example:**
```
🧠 TrustLink: Model Retrained Successfully - v2.20260205_143000

Performance Metrics:
- Accuracy: 94.5%
- Precision: 92.3%
- Recall: 89.7%

Training Samples: 1523
```

---

## 🧪 Testing Email Setup

### Test 1: Manual Python Test
```python
from email_notifier import EmailNotifier

notifier = EmailNotifier({
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'abcdefghijklmnop',
    'admin_email': 'admin@example.com',
    'enabled': True
})

# Test feedback notification
notifier.send_feedback_notification({
    'url': 'http://test-phishing.com',
    'original_prediction': 'Safe',
    'correct_label': 'Phishing',
    'feedback_type': 'correction',
    'username': 'test_user',
    'timestamp': '2026-02-05 14:30:00'
})
```

### Test 2: Submit Feedback via UI
1. Scan a URL in TrustLink
2. Click "Incorrect" or "Correct" button
3. Check your admin email inbox
4. Should receive formatted email within seconds

### Test 3: Check Console Logs
```
✅ Email sent to admin@example.com: ⚠️ TrustLink: INCORRECT PREDICTION - User Feedback
```

---

## 🔧 Troubleshooting

### "Email not configured - skipping notification"
**Solution:** Set environment variables and restart app

### "SMTPAuthenticationError"
**Solutions:**
- Gmail: Make sure you're using App Password, not regular password
- Check 2FA is enabled
- Verify credentials are correct

### "SMTPServerDisconnected"
**Solutions:**
- Check SMTP server and port
- Gmail: `smtp.gmail.com:587`
- Outlook: `smtp.office365.com:587`

### "Connection timed out"
**Solutions:**
- Check firewall settings
- Ensure port 587 is open
- Try alternative port 465 (SSL)

### Not receiving emails
**Solutions:**
- Check spam/junk folder
- Verify admin email is correct
- Test with Gmail account first
- Check console for error messages

---

## 🎨 Customizing Email Templates

Edit `email_notifier.py` to customize:

### Change Colors:
```python
# Line ~150: Header gradient
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Change Footer Text:
```python
# Line ~200: Footer section
<p>Your custom footer text here</p>
```

### Add Your Logo:
```python
# In HTML template
<img src="https://your-domain.com/logo.png" alt="Logo" style="max-width: 200px;">
```

---

## 📊 What Happens When?

### User Submits Feedback:
1. ✅ Feedback saved to database
2. ✅ Added to training data
3. 📧 Email sent to admin (if configured)
4. ✨ User sees "Thank you" message

### Admin Retrains Model:
1. 🔄 Model retrains with new data
2. 📊 Metrics calculated
3. 💾 New model saved
4. 📧 Email sent to admin (if configured)
5. 🚀 New model goes live immediately

---

## 🔐 Security Best Practices

### DO:
✅ Use App Passwords (not regular passwords)  
✅ Store credentials in environment variables  
✅ Use dedicated email account for sending  
✅ Enable 2FA on sender account  
✅ Keep sender password secure  

### DON'T:
❌ Commit credentials to Git  
❌ Use personal email password  
❌ Share sender credentials  
❌ Disable 2FA to avoid app passwords  
❌ Send sensitive data in emails  

---

## 🌟 Advanced Configuration

### Different Emails for Different Events

Edit `app.py`:
```python
# Separate admin emails
feedback_email = 'feedback@example.com'
retrain_email = 'ml-team@example.com'

# In feedback endpoint
email_notifier.send_email(
    to_email=feedback_email,
    subject='...',
    html_body='...'
)
```

### Add CC/BCC Recipients

Edit `email_notifier.py`:
```python
message['Cc'] = 'team@example.com'
message['Bcc'] = 'logs@example.com'
```

### Email Throttling (Prevent Spam)

```python
# Add to EmailNotifier class
from time import time

def __init__(self):
    self.last_sent = {}
    self.min_interval = 60  # 1 minute between emails

def should_send(self, email_type):
    now = time()
    last = self.last_sent.get(email_type, 0)
    if now - last < self.min_interval:
        return False
    self.last_sent[email_type] = now
    return True
```

---

## 📞 Support

### Common SMTP Settings

| Provider | SMTP Server | Port | SSL/TLS |
|----------|-------------|------|---------|
| Gmail | smtp.gmail.com | 587 | STARTTLS |
| Outlook | smtp.office365.com | 587 | STARTTLS |
| Yahoo | smtp.mail.yahoo.com | 587 | STARTTLS |
| SendGrid | smtp.sendgrid.net | 587 | STARTTLS |
| Mailgun | smtp.mailgun.org | 587 | STARTTLS |

### Getting Help

1. Check console output for detailed error messages
2. Test with Gmail first (easiest to set up)
3. Verify environment variables are set: `echo $env:SENDER_EMAIL`
4. Check `email_notifier.py` for debug prints

---

## ✅ Verification Checklist

- [ ] 2FA enabled on sender email
- [ ] App password generated
- [ ] Environment variables set
- [ ] TrustLink restarted
- [ ] Console shows "✓ Email notifications enabled"
- [ ] Test email sent successfully
- [ ] Email appears in inbox (check spam)
- [ ] HTML formatting looks correct

---

## 🎉 You're All Set!

Once configured, TrustLink will automatically:
- 📧 Email you when users report incorrect predictions
- 📧 Email you when model is retrained
- 📊 Help you track model improvement over time
- 🚀 Keep you informed about system activity

**The learning system is now complete with email notifications!** 🎊

# 👑 TrustLink Admin Account - Setup Complete

## 🎉 Your Admin Account is Ready!

### 📋 Login Credentials

```
URL:      http://localhost:5000/login
Username: admin
Password: Admin123!@#
```

⚠️ **IMPORTANT:** Change this password immediately after first login!

---

## 📊 Admin Dashboard Access

Once logged in, access your admin dashboard at:

**http://localhost:5000/admin**

---

## 🔐 Admin Privileges

As an administrator, you can:

### 1. **System Overview**
- View total users, scans, and threats blocked
- See new registrations and activity trends
- Monitor system health and performance

### 2. **User Management** (`/admin/users`)
- View all registered users
- See user verification status
- Check admin vs regular users
- View detailed user information
- See each user's scan history

### 3. **Scan History** (`/admin/scans`)
- View ALL scans from ALL users
- See what URLs users are checking
- Monitor phishing detection effectiveness
- Track suspicious activity

### 4. **User Details** (`/admin/users/{id}`)
- Detailed user profile
- Complete scan history for that user
- User statistics
- API keys created by user

### 5. **Analytics** (`/analytics`)
- System-wide analytics
- Trends over time
- Detection rates
- Usage patterns

---

## 🚀 Quick Start Guide

### Step 1: Login
1. Go to http://localhost:5000/login
2. Enter username: `admin`
3. Enter password: `Admin123!@#`
4. Click "Login"

### Step 2: Access Admin Dashboard
1. After login, go to http://localhost:5000/admin
2. You'll see system statistics and recent activity
3. Navigate using the admin menu

### Step 3: Explore Admin Features

**View All Users:**
- Click "Manage Users" or go to `/admin/users`
- See all registered users with their status

**View All Scans:**
- Click "All Scans" or go to `/admin/scans`
- See every URL scan from all users

**View User Details:**
- Click "View" next to any user
- See their complete profile and activity

---

## 🛡️ Security Best Practices

### Change Your Password
1. After first login, go to your dashboard
2. (Future feature: Password change in settings)
3. For now, update in database or use forgot password

### Keep Admin Credentials Secure
- Don't share admin credentials
- Use a strong, unique password
- Log out when done
- Monitor admin access logs

### Regular Monitoring
- Check system statistics regularly
- Review user activity
- Monitor for suspicious patterns
- Keep track of phishing detections

---

## 📈 Admin Dashboard Features

### System Statistics Cards
- **Total Users** - Number of registered users
- **Verified Users** - Users who verified their email
- **Total Scans** - All URL scans performed
- **Threats Blocked** - Phishing attempts detected

### Recent Users Table
Shows last 10 registered users with:
- User ID
- Username and email
- Verification status
- Admin role badge
- Registration date
- Quick action links

### Recent Scans Table
Shows last 20 scans with:
- Username (or Anonymous)
- URL scanned
- Detection result (Phishing/Safe)
- Confidence level
- Risk level
- Scan timestamp

---

## 🔧 Admin Routes Reference

| Route | Description |
|-------|-------------|
| `/admin` | Main admin dashboard |
| `/admin/users` | All users list (paginated) |
| `/admin/users/{id}` | Detailed user profile |
| `/admin/scans` | All scans list (paginated) |
| `/analytics` | System analytics (also for users) |
| `/dashboard` | Your personal dashboard |

---

## 💡 Tips & Tricks

### Quick Navigation
- Bookmark `/admin` for quick access
- Use browser's back button to navigate
- Click TrustLink logo to go home

### Data Analysis
- Export scan data for analysis (future feature)
- Monitor trends over time
- Identify power users
- Track detection accuracy

### User Support
- View user's scan history to help troubleshoot
- Check if user verified their email
- Monitor API key usage

---

## 🐛 Troubleshooting

### Can't Access Admin Dashboard?
1. Make sure you're logged in with admin account
2. Verify `is_admin = 1` in database
3. Clear browser cache and try again

### Forgot Admin Password?
Run this to reset it:
```bash
python -c "from database import Database; db = Database(); db.reset_password_for_user('admin', 'NewPassword123!@#')"
```

Or update `setup_admin.py` with new password and run it.

### Database Error?
Make sure database schema is up to date:
```bash
python -c "from database import Database; db = Database()"
```

---

## 📞 Need Help?

- Check `IMPROVEMENTS_SUMMARY_v2.md` for feature docs
- See `QUICK_START_v2.1.md` for setup guide
- Review database schema in `database.py`

---

## 🎯 Next Steps

1. ✅ Login with admin credentials
2. ✅ Explore admin dashboard
3. ✅ View user list
4. ✅ Check scan history
5. ⚠️ Change default password
6. 📧 Set up email notifications (see `.env` file)
7. 🔒 Configure security settings
8. 📊 Monitor system regularly

---

**Enjoy your admin powers! 👑**

Remember: With great power comes great responsibility!

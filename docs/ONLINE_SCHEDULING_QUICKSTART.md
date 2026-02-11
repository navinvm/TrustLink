# 🌐 Quick Start - Online Deployment Scheduling

## ⚡ Easiest Method (Works Everywhere)

Your TrustLink app now includes a **built-in background scheduler** that runs daily training automatically!

### **3-Step Setup:**

#### **1. Enable Continuous Learning**

Add to your `.env` file (or platform environment variables):

```bash
ENABLE_CONTINUOUS_LEARNING=true
```

#### **2. Install APScheduler**

```bash
pip install APScheduler==3.10.4
```

#### **3. Deploy**

```bash
git add .
git commit -m "Enable continuous learning"
git push
```

**That's it!** ✅

---

## 🎯 How It Works

When your app starts online:

1. Background scheduler automatically starts
2. Schedules daily training at **2:00 AM UTC**
3. Every 24 hours:
   - Collects 500 fresh phishing URLs
   - Generates 300 safe URLs
   - Gets user feedback
   - Triple-verifies with all APIs
   - Retrains model
   - Updates accuracy

---

## 📋 Platform-Specific Instructions

### **Heroku**

```bash
# Set environment variable
heroku config:set ENABLE_CONTINUOUS_LEARNING=true

# Deploy
git push heroku main
```

### **Railway**

```bash
# In Railway dashboard:
# Variables → Add: ENABLE_CONTINUOUS_LEARNING=true

# Deploy
railway up
```

### **Render/Vercel/Netlify**

```bash
# In platform dashboard:
# Environment Variables → Add:
# ENABLE_CONTINUOUS_LEARNING=true
```

### **AWS/DigitalOcean/VPS**

```bash
# Add to .env file
echo "ENABLE_CONTINUOUS_LEARNING=true" >> .env

# Restart app
pm2 restart trustlink
```

---

## 🔍 Verify It's Working

### **Check Logs:**

Your app will show this on startup:

```
✅ Continuous learning enabled - Next training: 2026-02-10 02:00:00
```

### **Check Next Run:**

Visit your app and look for:
- Updated accuracy after 2 AM UTC each day
- Training logs in console

---

## ⚙️ Advanced Options

### **Change Training Time:**

Edit `background_scheduler.py`:

```python
# Change from 2 AM to 3 AM UTC
CronTrigger(hour=3, minute=0)
```

### **Adjust Data Limits:**

Edit `background_scheduler.py`:

```python
phishing_limit=1000,  # More phishing URLs
safe_limit=200        # More safe URLs
```

### **Disable Temporarily:**

```bash
# Set to false
ENABLE_CONTINUOUS_LEARNING=false
```

---

## 💰 Cost Impact

- **CPU**: 15-20 minutes once per day
- **Memory**: +500MB during training (released after)
- **Network**: ~50MB download per day
- **Storage**: ~5MB per day

**Total cost increase**: < $1/month on most platforms

---

## ✅ You're Done!

Your model will now:
- ✅ Train automatically every 24 hours
- ✅ Learn from fresh phishing URLs
- ✅ Incorporate user feedback
- ✅ Update accuracy in real-time
- ✅ Get smarter every single day

**No manual work required!** 🚀

---

## 📚 More Info

- **Detailed setup**: `docs/ONLINE_DEPLOYMENT_SCHEDULING.md`
- **How it works**: `CONTINUOUS_LEARNING_README.md`
- **Troubleshooting**: `docs/CONTINUOUS_LEARNING_SETUP.md`

---

**Questions?** The scheduler runs in the background automatically. Just set `ENABLE_CONTINUOUS_LEARNING=true` and deploy! ✨

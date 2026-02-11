# ⚡ Quick Deploy - TrustLink in 5 Minutes

## 🚀 Deploy to Railway (Fastest & Free)

### Step 1: Push to GitHub (2 minutes)
```powershell
# If git is not initialized
git init

# Add all files
git add .

# Commit
git commit -m "Deploy TrustLink"

# Create GitHub repo and push
# Go to: https://github.com/new
# Then:
git remote add origin https://github.com/YOUR_USERNAME/trustlink.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway (3 minutes)
1. **Go to**: https://railway.app/new
2. **Login** with GitHub
3. **Deploy from GitHub repo** → Select your `trustlink` repo
4. **Add Variables**:
   - Click "Variables" tab
   - Add: `SECRET_KEY` = `change-this-to-random-string`
   - Add: `FLASK_ENV` = `production`
5. **Done!** Railway gives you a URL like:
   ```
   https://trustlink-production.up.railway.app
   ```

### Step 3: Generate Better Domain (30 seconds)
- Railway Settings → "Generate Domain"
- Get something like: `https://trustlink.railway.app`

---

## 🎯 That's It! You're Live!

✅ Your TrustLink is now online and accessible worldwide!

**What You Get:**
- ✅ Free HTTPS (SSL certificate)
- ✅ Automatic deployments when you push to GitHub
- ✅ 500 hours/month free (enough for personal projects)
- ✅ Live URL to share with anyone

---

## 🧪 Test Your Live Site

Visit your Railway URL and test:
1. ✅ Register a new account
2. ✅ Login
3. ✅ Scan a URL: `https://google.com`
4. ✅ Check Analytics page
5. ✅ Submit feedback

---

## 🔧 Common Issues & Fixes

### Issue: "Application failed to respond"
**Fix:** Check Railway logs
- Railway Dashboard → Logs
- Look for errors
- Usually missing dependencies or port issues

### Issue: Models not loading
**Fix:** Ensure `models/` folder is pushed to GitHub
```powershell
# Check if models exist
ls models/

# If missing, create dummy models or use the existing ones
git add models/
git commit -m "Add ML models"
git push
```

### Issue: Database resets on redeploy
**Expected behavior** on free tier!
**Fix:** Upgrade to Railway PostgreSQL (still free):
1. Railway Dashboard → New → Database → Add PostgreSQL
2. Connect to your app
3. Update code to use PostgreSQL URL

---

## 📈 Next Steps

1. **Custom Domain** (optional):
   - Buy domain ($10/year)
   - Add to Railway settings
   
2. **Monitor Your App**:
   - Check Railway logs regularly
   - Monitor usage stats
   
3. **Update Your App**:
   ```powershell
   # Make changes locally
   git add .
   git commit -m "Update feature X"
   git push
   # Railway auto-deploys!
   ```

---

## 💡 Pro Tips

✅ **Use PostgreSQL** instead of SQLite for production
✅ **Set strong SECRET_KEY** in environment variables
✅ **Monitor logs** for errors
✅ **Enable metrics** in Railway dashboard
✅ **Backup database** regularly

---

## 🎉 Share Your Link!

Your TrustLink is now live! Share it:
- On LinkedIn
- In your portfolio
- With friends
- In your resume

**Example:**
"Built and deployed a phishing detection system using ML"
🔗 https://trustlink.railway.app

---

Need the full deployment guide? See **DEPLOYMENT_GUIDE.md**

# 🚀 TrustLink Deployment Guide

Deploy TrustLink online for **FREE** using Railway or Render!

---

## 🎯 Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)

#### Step 1: Prepare Your Repository
1. Create a GitHub account if you don't have one: https://github.com/signup
2. Create a new repository:
   - Go to https://github.com/new
   - Name it: `trustlink-phishing-detector`
   - Make it **Public** or **Private** (your choice)
   - Click "Create repository"

3. Upload your code to GitHub:
   ```powershell
   # Initialize git (if not already done)
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit - TrustLink deployment ready"
   
   # Add your GitHub repository
   git remote add origin https://github.com/YOUR_USERNAME/trustlink-phishing-detector.git
   
   # Push to GitHub
   git push -u origin main
   ```

#### Step 2: Deploy to Railway
1. **Sign up for Railway**: https://railway.app/
   - Click "Login with GitHub"
   - Authorize Railway to access your GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `trustlink-phishing-detector` repository

3. **Configure Environment Variables**:
   - Railway will auto-detect Python and start building
   - Click on your project → "Variables" tab
   - Add these environment variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-key-change-this-in-production
   DATABASE_PATH=trustlink.db
   ```

4. **Deploy**!
   - Railway will automatically deploy
   - You'll get a URL like: `https://trustlink-production.up.railway.app`
   - Your app is now LIVE! 🎉

#### Step 3: Custom Domain (Optional)
- In Railway settings → "Domains"
- Click "Generate Domain" for a better subdomain
- Or connect your own custom domain

---

### Option 2: Render

#### Step 1: Prepare GitHub (Same as Railway above)

#### Step 2: Deploy to Render
1. **Sign up for Render**: https://render.com/
   - Click "Get Started for Free"
   - Sign in with GitHub

2. **Create New Web Service**:
   - Dashboard → "New +" → "Web Service"
   - Connect your `trustlink-phishing-detector` repository

3. **Configure the Service**:
   - **Name**: `trustlink-detector`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. **Environment Variables**:
   - Click "Advanced" → "Add Environment Variable"
   ```
   FLASK_APP=app.py
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-key-change-this
   DATABASE_PATH=trustlink.db
   ```

5. **Deploy**!
   - Click "Create Web Service"
   - Render builds and deploys automatically
   - Get URL like: `https://trustlink-detector.onrender.com`

---

## ✅ Post-Deployment Checklist

### 1. Test Your Live Site
- Visit your Railway/Render URL
- Register a new account
- Scan a test URL (try: `https://google.com`)
- Check analytics page
- Test feedback submission

### 2. Security Hardening
Update your environment variables:
```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to Railway/Render environment variables
SECRET_KEY=<generated-key-here>
```

### 3. Database Persistence (Important!)
⚠️ **Railway/Render free tier may lose database on redeploy**

**Solutions:**
- Use **Railway's PostgreSQL** (free tier):
  1. Add PostgreSQL service in Railway
  2. Connect to your app
  3. Update `database.py` to use PostgreSQL instead of SQLite

- Or use **external database**:
  - Supabase (free PostgreSQL): https://supabase.com
  - PlanetScale (free MySQL): https://planetscale.com

### 4. Enable HTTPS
✅ Railway and Render automatically provide HTTPS!
Your site will be secure by default.

### 5. Monitor Your App
**Railway:**
- View logs in real-time from dashboard
- Monitor CPU and memory usage
- Set up alerts

**Render:**
- Check logs under "Logs" tab
- Monitor metrics in dashboard

---

## 🎨 Custom Domain Setup (Optional)

### Buy a Domain ($10-15/year)
- Namecheap: https://namecheap.com
- Google Domains: https://domains.google
- Cloudflare: https://cloudflare.com

### Connect to Railway
1. Railway Dashboard → Your Project → Settings → Domains
2. Click "Custom Domain"
3. Add your domain: `trustlink.com`
4. Add DNS records from your domain registrar:
   ```
   Type: CNAME
   Name: @ (or www)
   Value: <your-railway-domain>.up.railway.app
   ```

### Connect to Render
1. Render Dashboard → Your Service → Settings
2. "Custom Domains" → "Add Custom Domain"
3. Follow DNS setup instructions

---

## 📊 Free Tier Limits

### Railway Free Tier
- ✅ 500 hours/month (about 21 days)
- ✅ $5 free credit/month
- ✅ Auto-sleep after inactivity
- ✅ 1GB RAM
- ✅ 1GB disk

### Render Free Tier
- ✅ 750 hours/month
- ⚠️ Auto-sleep after 15 min inactivity
- ⚠️ Cold starts (slow first load)
- ✅ 512MB RAM
- ✅ 1GB disk

---

## 🐛 Troubleshooting

### Issue: "Application Error" or 500 Error
**Fix:**
1. Check logs in Railway/Render dashboard
2. Ensure all dependencies in `requirements.txt`
3. Verify environment variables are set

### Issue: Database not persisting
**Fix:**
- Use PostgreSQL instead of SQLite
- Follow database persistence guide above

### Issue: Slow loading (Render)
**Expected:** Free tier sleeps after 15 min
- First load takes 30-60 seconds (cold start)
- Subsequent loads are fast

### Issue: Port binding error
**Fix:**
- Railway/Render automatically set `$PORT`
- Ensure `Procfile` uses `$PORT`

---

## 🚀 Upgrade Options (If Needed)

### Railway Pro ($20/month)
- No sleep
- More resources
- Better performance

### Render Paid ($7+/month)
- No sleep
- Faster cold starts
- More RAM/CPU

---

## 📞 Support

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Render:**
- Docs: https://render.com/docs
- Support: https://render.com/support

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Deployed to Railway or Render
- [ ] Environment variables configured
- [ ] Site is accessible via URL
- [ ] Can register and login
- [ ] URL scanning works
- [ ] Analytics page loads
- [ ] Feedback submission works
- [ ] HTTPS is enabled (check padlock in browser)

---

## 🎉 You're Live!

Your TrustLink phishing detector is now online and accessible to anyone!

**Share your link:**
- Railway: `https://trustlink-production.up.railway.app`
- Render: `https://trustlink-detector.onrender.com`

**Next Steps:**
1. Share with friends/colleagues
2. Add to your portfolio
3. Monitor usage in analytics
4. Consider custom domain
5. Upgrade if you need 24/7 uptime

---

**Need help?** Check the logs in your Railway/Render dashboard or review the troubleshooting section above.

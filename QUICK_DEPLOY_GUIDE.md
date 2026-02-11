# TrustLink Quick Deployment Guide

## 🚀 Deploy in 5 Minutes

### Option 1: Railway + Vercel (Recommended)

Perfect for production - combines Railway's database with Vercel's global CDN.

#### Step 1: Deploy Railway (Backend + Database)

1. **Go to Railway**: [railway.app/new](https://railway.app/new)
   
2. **Deploy from GitHub**:
   - Click "Deploy from GitHub repo"
   - Select `navinvm/TrustLink`
   - Click "Deploy Now"

3. **Add PostgreSQL Database**:
   - In your project, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway auto-connects it

4. **Set Environment Variables**:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key-here
   AUTO_ML_TRAINING=true
   ```

5. **Get Your Railway Database URL**:
   - Click PostgreSQL service
   - Go to "Variables" tab
   - Copy `DATABASE_URL` value
   - Save it for Vercel setup

#### Step 2: Deploy Vercel (Frontend + API)

1. **Go to Vercel**: [vercel.com/new](https://vercel.com/new)

2. **Import Project**:
   - Click "Add New" → "Project"
   - Select `navinvm/TrustLink`
   - Click "Import"

3. **Set Environment Variables**:
   - Click "Environment Variables"
   - Add these variables:
   
   ```
   DATABASE_URL=paste-railway-database-url-here
   SECRET_KEY=same-as-railway-secret-key
   FLASK_ENV=production
   AUTO_ML_TRAINING=false
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes

#### Step 3: Test Your Deployment

**Vercel URL** (Frontend/API):
```
https://your-project.vercel.app
```
- Test phishing detection
- Fast global CDN

**Railway URL** (Backend):
```
https://your-project.railway.app
```
- Full authentication
- User dashboard
- Admin panel

---

### Option 2: Railway Only (Simple)

Good for getting started quickly without complexity.

1. **Go to Railway**: [railway.app/new](https://railway.app/new)

2. **Deploy from GitHub**:
   - Select `navinvm/TrustLink`
   - Click "Deploy Now"

3. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "PostgreSQL"

4. **Set Variables**:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   AUTO_ML_TRAINING=true
   ```

5. **Access Your App**:
   - Railway generates a URL automatically
   - Visit it and start using TrustLink!

---

### Option 3: Vercel Only (API-Only)

Lightweight deployment for phishing detection API only.

1. **Go to Vercel**: [vercel.com/new](https://vercel.com/new)

2. **Import `navinvm/TrustLink`**

3. **Deploy**:
   - No additional config needed
   - Uses in-memory database
   - No user authentication

4. **Use as API**:
   ```bash
   curl -X POST https://your-app.vercel.app/predict \
     -H "Content-Type: application/json" \
     -d '{"url": "example.com"}'
   ```

---

## 🎯 Which Option Should I Choose?

| Use Case | Recommended Option | Why |
|----------|-------------------|-----|
| **Production App** | Railway + Vercel | Best performance + global CDN |
| **Getting Started** | Railway Only | Simplest setup |
| **API Service** | Vercel Only | Fast, auto-scaling |
| **Full Control** | Railway Only | All features enabled |

---

## 📋 Post-Deployment Checklist

After deployment, verify these work:

- [ ] Homepage loads
- [ ] Phishing detection works
- [ ] User registration works
- [ ] Login/logout works
- [ ] Scan history saves
- [ ] Browser extension connects

---

## 🔧 Common Setup Issues

### Issue: "Database connection failed"
**Solution**: Make sure `DATABASE_URL` is set correctly in environment variables

### Issue: "Secret key not set"
**Solution**: Add `SECRET_KEY` environment variable (minimum 32 characters)

### Issue: Vercel shows "Application failed to initialize"
**Solution**: Check that all environment variables are set, especially `DATABASE_URL`

### Issue: Railway shows "Build failed"
**Solution**: Check Railway logs, might need to add `psycopg2-binary` to requirements.txt

---

## 🔐 Security Notes

### Generate a Secure Secret Key

```bash
# On Linux/Mac
python -c "import secrets; print(secrets.token_hex(32))"

# On Windows PowerShell
python -c "import secrets; print(secrets.token_hex(32))"
```

### Important Security Steps

1. ✅ Use HTTPS (both platforms provide this automatically)
2. ✅ Set strong `SECRET_KEY`
3. ✅ Never commit `.env` files to Git
4. ✅ Use environment variables for all secrets
5. ✅ Enable `SESSION_COOKIE_SECURE=true` in production

---

## 📊 Monitoring Your Deployment

### Railway Dashboard
- View deployment logs
- Monitor database size
- Check resource usage

### Vercel Dashboard
- Function logs
- Analytics
- Performance metrics

---

## 🔄 Updating Your Deployment

Both platforms auto-deploy when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push
```

- Railway: Rebuilds automatically
- Vercel: Rebuilds automatically

---

## 💰 Cost Breakdown

### Free Tier Limits

**Railway**:
- $5 free credit/month
- Includes PostgreSQL
- ~500 hours uptime

**Vercel**:
- 100 GB bandwidth
- Unlimited static hosting
- 100 serverless hours/month

**Total**: FREE for small projects!

---

## 🆘 Need Help?

1. Check the logs in your platform dashboard
2. Read `DEPLOYMENT_ARCHITECTURE.md` for details
3. Open an issue on GitHub
4. Check Railway/Vercel documentation

---

## 🎉 You're Done!

Your TrustLink app is now live and ready to protect users from phishing attacks!

**Share your deployment**:
- Vercel: `https://your-project.vercel.app`
- Railway: `https://your-project.railway.app`

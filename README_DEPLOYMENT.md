# TrustLink Deployment Documentation

## 📚 Complete Deployment Guide

This directory contains everything you need to deploy TrustLink to production.

### 📖 Documentation Files

1. **[QUICK_DEPLOY_GUIDE.md](QUICK_DEPLOY_GUIDE.md)** - Start here!
   - 5-minute deployment walkthrough
   - Step-by-step instructions
   - Common issues & solutions

2. **[DEPLOYMENT_ARCHITECTURE.md](DEPLOYMENT_ARCHITECTURE.md)** - Architecture deep-dive
   - System architecture diagram
   - Platform comparison
   - Data flow explanation
   - Cost breakdown

3. **Environment Templates**:
   - `.env.example.railway` - Railway configuration
   - `.env.example.vercel` - Vercel configuration
   - `.env.example` - Local development

---

## 🚀 Quick Start

### Deploy to Railway + Vercel (Recommended)

```bash
# 1. Deploy to Railway
Visit: https://railway.app/new
Select: navinvm/TrustLink
Add: PostgreSQL database

# 2. Deploy to Vercel
Visit: https://vercel.com/new
Import: navinvm/TrustLink
Add DATABASE_URL from Railway

# Done! 🎉
```

---

## 🏗️ Architecture Overview

```
┌──────────┐
│  Users   │
└────┬─────┘
     │
     ▼
┌─────────────────┐         ┌──────────────────┐
│  Vercel (CDN)   │────────▶│ Railway (Backend)│
│  - Frontend     │         │  - PostgreSQL DB │
│  - API Layer    │         │  - Full App      │
└─────────────────┘         └──────────────────┘
```

**Benefits**:
- ⚡ Fast global CDN (Vercel)
- 💾 Persistent database (Railway)
- 🔄 Auto-scaling (both platforms)
- 🆓 Free tier available

---

## 📋 Deployment Options

| Option | Best For | Setup Time | Free Tier |
|--------|----------|------------|-----------|
| **Railway + Vercel** | Production | 5 min | ✅ Yes |
| **Railway Only** | Simple apps | 3 min | ✅ Yes |
| **Vercel Only** | API service | 2 min | ✅ Yes |

---

## 🔧 Configuration Files

### Railway
- `railway.json` - Railway-specific config
- `Procfile` - Process definition
- `gunicorn_config.py` - Gunicorn settings
- `requirements.txt` - Python dependencies

### Vercel
- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function handler
- `api/requirements.txt` - Vercel dependencies

### Database
- `database.py` - SQLite (local/Vercel)
- `railway_database.py` - PostgreSQL (Railway)
- `unified_database.py` - Auto-detection layer

---

## 🔐 Environment Variables

### Required (All Platforms)
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-min-32-chars
```

### Railway-Specific
```bash
DATABASE_URL=postgresql://...  # Auto-set by Railway
AUTO_ML_TRAINING=true
```

### Vercel-Specific
```bash
DATABASE_URL=postgresql://...  # Copy from Railway
AUTO_ML_TRAINING=false
```

---

## ✅ Post-Deployment Checklist

After deploying, verify:

- [ ] Health endpoint works: `/health`
- [ ] Homepage loads
- [ ] Phishing detection API works: `/predict`
- [ ] User registration works (if using Railway DB)
- [ ] Login works
- [ ] Scan history saves
- [ ] Browser extension can connect

---

## 📊 Monitoring

### Railway
- Dashboard: `railway.app/dashboard`
- Logs: Real-time in dashboard
- Metrics: CPU, memory, database

### Vercel
- Dashboard: `vercel.com/dashboard`
- Functions: Execution logs
- Analytics: Traffic & performance

---

## 🔄 Updates & Maintenance

### Automatic Deployment
Both platforms auto-deploy on `git push`:

```bash
git add .
git commit -m "Update"
git push origin main
```

### Manual Deployment
- **Railway**: Click "Deploy" in dashboard
- **Vercel**: Click "Redeploy" in deployments

---

## 🐛 Troubleshooting

### Common Issues

**"Database connection failed"**
- ✅ Check `DATABASE_URL` is set
- ✅ Verify Railway PostgreSQL is running
- ✅ Check Railway database is not sleeping

**"Application failed to initialize"**
- ✅ Check all environment variables are set
- ✅ Review deployment logs
- ✅ Verify `SECRET_KEY` is configured

**"Model not found"**
- ✅ Ensure `models/` directory is included
- ✅ Check `.vercelignore` doesn't exclude models
- ✅ Verify models are in repository

---

## 💰 Cost Estimate

### Free Tier (Perfect for Testing)
- Railway: $5 credit/month
- Vercel: 100GB bandwidth/month
- **Total: FREE** within limits

### Production (Paid Plans)
- Railway: ~$20/month (database + app)
- Vercel: ~$20/month (Pro plan)
- **Total: ~$40/month**

---

## 🆘 Support

1. **Read the guides**: Start with `QUICK_DEPLOY_GUIDE.md`
2. **Check logs**: Platform dashboards have detailed logs
3. **Platform docs**:
   - Railway: [docs.railway.app](https://docs.railway.app)
   - Vercel: [vercel.com/docs](https://vercel.com/docs)
4. **Open an issue**: GitHub repository

---

## 🎯 Next Steps

1. ✅ Choose your deployment option
2. ✅ Follow the Quick Deploy Guide
3. ✅ Set up environment variables
4. ✅ Test your deployment
5. 📈 Monitor and scale as needed

---

## 📦 What's Included

```
TrustLink/
├── 📄 QUICK_DEPLOY_GUIDE.md      # Start here
├── 📄 DEPLOYMENT_ARCHITECTURE.md # Deep dive
├── 📄 README_DEPLOYMENT.md       # This file
├── 🔧 railway.json               # Railway config
├── 🔧 vercel.json                # Vercel config
├── 🔧 railway_database.py        # PostgreSQL support
├── 🔧 unified_database.py        # Auto-detection
├── 📝 .env.example.railway       # Railway env vars
├── 📝 .env.example.vercel        # Vercel env vars
└── 📁 api/                       # Vercel functions
    ├── index.py                  # Main handler
    └── requirements.txt          # Dependencies
```

---

## 🌟 Success!

Once deployed, your TrustLink app will:
- ✅ Detect phishing URLs globally
- ✅ Serve users from the nearest edge location
- ✅ Scale automatically with demand
- ✅ Maintain persistent user data
- ✅ Protect users 24/7

**Ready to deploy?** Start with [QUICK_DEPLOY_GUIDE.md](QUICK_DEPLOY_GUIDE.md)!

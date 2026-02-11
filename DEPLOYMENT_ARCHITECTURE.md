# TrustLink Deployment Architecture

## Overview

TrustLink uses a **hybrid deployment architecture** for optimal performance and scalability:

- **Railway**: Backend database (PostgreSQL) + Full application server
- **Vercel**: Frontend/API layer with serverless functions

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Frontend/API)                     │
│  • Serverless Functions (phishing detection)                │
│  • Static Content (landing pages, assets)                   │
│  • CDN Distribution (global edge network)                   │
│  • Connects to Railway for database operations              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ DATABASE_URL
┌─────────────────────────────────────────────────────────────┐
│                    Railway (Backend)                         │
│  • PostgreSQL Database (persistent storage)                 │
│  • Full Flask Application (with auth, history, etc.)        │
│  • Background ML Training Scheduler                         │
│  • API Keys & User Management                               │
└─────────────────────────────────────────────────────────────┘
```

## Platform Comparison

| Feature                  | Railway | Vercel |
|--------------------------|---------|--------|
| **Database**             | PostgreSQL (persistent) | Connects to Railway |
| **Filesystem**           | ✅ Writable | ❌ Read-only |
| **User Authentication**  | ✅ Full support | ✅ Via Railway DB |
| **Scan History**         | ✅ Persistent | ✅ Via Railway DB |
| **ML Model Loading**     | ✅ From files | ✅ From bundled files |
| **Background Jobs**      | ✅ Enabled | ❌ Disabled |
| **Auto-scaling**         | Manual | ✅ Automatic |
| **Global CDN**           | No | ✅ Yes |
| **Cold Start**           | ~1s | ~200ms |

## Deployment Modes

### 1. **Railway Only** (Standalone)
- Full-featured application
- PostgreSQL database
- Background ML training
- No CDN benefits

### 2. **Vercel Only** (Serverless)
- Phishing detection API
- No persistent database
- No user authentication
- Global CDN

### 3. **Railway + Vercel** (Recommended)
- Railway: Database + Backend
- Vercel: Frontend + Fast API
- Best performance
- Automatic scaling

## Environment Variables

### Railway Configuration

```bash
# Database (automatically provided by Railway)
DATABASE_URL=postgresql://user:pass@host:5432/railway

# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Features
AUTO_ML_TRAINING=true
USE_REDIS=false
```

### Vercel Configuration

```bash
# Database (connect to Railway)
DATABASE_URL=postgresql://user:pass@railway.host:5432/railway

# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Serverless-specific
AUTO_ML_TRAINING=false
VERCEL=1
```

## Setup Instructions

### Step 1: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your TrustLink repository
4. Add PostgreSQL database:
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
5. Railway will automatically set `DATABASE_URL`

### Step 2: Deploy to Vercel

1. Go to [Vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your TrustLink repository
4. Configure environment variables:
   - `DATABASE_URL`: Copy from Railway (see below)
   - `SECRET_KEY`: Same as Railway
   - `FLASK_ENV`: production

### Step 3: Get Railway Database URL

In Railway dashboard:
1. Click on PostgreSQL service
2. Go to "Variables" tab
3. Copy `DATABASE_URL`
4. Add it to Vercel environment variables

### Step 4: Configure Domain (Optional)

**Railway:**
- Click "Settings" → "Generate Domain"
- Use for API: `https://your-app.railway.app`

**Vercel:**
- Automatic domain: `https://your-app.vercel.app`
- Add custom domain in settings

## API Endpoints

### Vercel (Frontend/Fast API)
```
https://trustlink.vercel.app/
├── /                    # Landing page
├── /predict             # Phishing detection (fast)
└── /api/health          # Health check
```

### Railway (Backend/Full App)
```
https://trustlink.railway.app/
├── /login               # User authentication
├── /register            # User registration
├── /dashboard           # User dashboard
├── /history             # Scan history
├── /api/keys            # API key management
└── /admin               # Admin panel
```

## How Data Flows

1. **User visits Vercel** → Fast global CDN
2. **Phishing check** → Runs on Vercel serverless
3. **Login/Register** → Connects to Railway database
4. **Save scan history** → Stores in Railway PostgreSQL
5. **View history** → Fetches from Railway database

## Cost Estimate

### Free Tier (Hobby Projects)

- **Railway**: $5/month credit (includes database)
- **Vercel**: Free (100GB bandwidth, 100 serverless invocations/day)
- **Total**: ~$5/month or FREE within limits

### Production (Paid)

- **Railway**: $20/month (database + app)
- **Vercel**: $20/month (Pro plan)
- **Total**: ~$40/month

## Monitoring

### Railway
- Built-in metrics dashboard
- Deployment logs
- Database metrics

### Vercel
- Function logs
- Analytics
- Performance metrics

## Backup Strategy

### Database Backups (Railway)
```bash
# Railway provides automatic daily backups
# Manual backup:
pg_dump $DATABASE_URL > backup.sql
```

### Code Backups
- GitHub repository (automatic)
- Both platforms deploy from Git

## Troubleshooting

### Issue: Vercel can't connect to Railway database
**Solution**: Ensure `DATABASE_URL` is correctly set in Vercel environment variables

### Issue: Database connection timeout
**Solution**: Railway database might be sleeping (free tier). Wake it up or upgrade.

### Issue: Vercel function timeout
**Solution**: Reduce model size or use Railway for heavy ML operations

## Security

### Railway
- Database credentials auto-generated
- Private networking between services
- SSL/TLS encryption

### Vercel
- Environment variables encrypted
- Automatic HTTPS
- DDoS protection

## Next Steps

1. ✅ Deploy Railway database
2. ✅ Deploy Vercel frontend
3. ✅ Connect them with DATABASE_URL
4. 🔄 Monitor performance
5. 📈 Scale as needed

## Support

- Railway: [docs.railway.app](https://docs.railway.app)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
- TrustLink: Check repository issues

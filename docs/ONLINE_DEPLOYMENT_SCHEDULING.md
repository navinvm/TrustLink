# 🌐 Online Deployment - Continuous Learning Setup

## Overview

When TrustLink is deployed online (Heroku, Railway, AWS, etc.), you can schedule automatic daily training using several methods.

## 🎯 Best Options by Platform

### **Option 1: Background Scheduler (Built-in)** ⭐ EASIEST

Uses APScheduler to run training in the background while your app is running.

#### **Setup:**

1. **Add to `.env` file:**
   ```bash
   ENABLE_CONTINUOUS_LEARNING=true
   ```

2. **Install dependencies:**
   ```bash
   pip install APScheduler==3.10.4
   ```

3. **Deploy your app** - That's it! 🎉

#### **How it works:**
- Scheduler starts automatically when app starts
- Runs daily at 2:00 AM UTC
- No external services needed
- Works on ANY platform

#### **Pros:**
- ✅ No setup needed
- ✅ Works everywhere
- ✅ Free
- ✅ Self-contained

#### **Cons:**
- ⚠️ Only runs when app is running
- ⚠️ Restarts reset the schedule

---

### **Option 2: Platform-Specific Schedulers**

#### **Heroku (Heroku Scheduler Add-on)**

1. **Add the scheduler add-on:**
   ```bash
   heroku addons:create scheduler:standard
   ```

2. **Open scheduler dashboard:**
   ```bash
   heroku addons:open scheduler
   ```

3. **Add a job:**
   - **Command:** `python scheduled_training.py`
   - **Frequency:** Daily
   - **Time:** 2:00 AM UTC

4. **Save** - Done!

**Cost:** Free tier available

---

#### **Railway**

1. **Create a new service** (separate from web app)
   - Type: Cron Job
   - Name: `trustlink-training`

2. **Add schedule:**
   ```
   0 2 * * * python scheduled_training.py
   ```

3. **Environment:** Use same `.env` as main app

4. **Deploy** - Done!

**Cost:** Billed per execution time

---

#### **AWS (EventBridge + Lambda)**

1. **Create Lambda function:**
   ```python
   # lambda_function.py
   import json
   import subprocess
   
   def lambda_handler(event, context):
       result = subprocess.run(['python', 'scheduled_training.py'], 
                              capture_output=True, text=True)
       return {
           'statusCode': 200,
           'body': json.dumps(result.stdout)
       }
   ```

2. **Create EventBridge rule:**
   - Schedule: `cron(0 2 * * ? *)`  (2 AM UTC daily)
   - Target: Your Lambda function

3. **Deploy** - Done!

**Cost:** ~$0.01/day

---

#### **Google Cloud (Cloud Scheduler)**

1. **Create Cloud Scheduler job:**
   ```bash
   gcloud scheduler jobs create http trustlink-training \
       --schedule="0 2 * * *" \
       --uri="https://your-app.com/api/run-training" \
       --http-method=POST \
       --headers="X-Training-Secret=YOUR_SECRET"
   ```

2. **Add endpoint to app.py:**
   ```python
   @app.route('/api/run-training', methods=['POST'])
   def trigger_training():
       secret = request.headers.get('X-Training-Secret')
       if secret != os.environ.get('TRAINING_SECRET'):
           return jsonify({'error': 'Unauthorized'}), 401
       
       # Run training in background thread
       from threading import Thread
       from scheduled_training import ContinuousLearningSystem
       
       def run():
           system = ContinuousLearningSystem()
           system.run_daily_training()
       
       Thread(target=run).start()
       return jsonify({'status': 'started'})
   ```

3. **Deploy** - Done!

**Cost:** Free tier available

---

#### **DigitalOcean (Cron Job Droplet)**

1. **SSH into your droplet:**
   ```bash
   ssh root@your-droplet-ip
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add daily job:**
   ```bash
   0 2 * * * cd /var/www/trustlink && /usr/bin/python3 scheduled_training.py >> /var/log/training.log 2>&1
   ```

4. **Save** - Done!

**Cost:** Included with droplet

---

### **Option 3: External Cron Services**

#### **EasyCron** (Free tier)

1. **Sign up:** https://www.easycron.com
2. **Create new job:**
   - URL: `https://your-app.com/api/run-training`
   - Schedule: Daily at 2:00 AM
   - Method: POST
   - Headers: `X-Training-Secret: YOUR_SECRET`

3. **Save** - Done!

---

#### **Cron-Job.org** (Free)

1. **Sign up:** https://cron-job.org
2. **Create new cron job:**
   - URL: `https://your-app.com/api/run-training`
   - Schedule: `0 2 * * *`
   - Method: POST

3. **Save** - Done!

---

## 📋 Comparison Table

| Method | Cost | Setup | Reliability | Best For |
|--------|------|-------|-------------|----------|
| **Built-in Scheduler** | Free | 1 min | ⭐⭐⭐ | Any platform |
| **Heroku Scheduler** | Free/Paid | 5 min | ⭐⭐⭐⭐⭐ | Heroku |
| **Railway Cron** | Per-use | 3 min | ⭐⭐⭐⭐ | Railway |
| **AWS EventBridge** | ~$0.01/day | 15 min | ⭐⭐⭐⭐⭐ | AWS |
| **Google Cloud** | Free tier | 10 min | ⭐⭐⭐⭐⭐ | GCP |
| **DigitalOcean** | Included | 5 min | ⭐⭐⭐⭐ | Droplet |
| **EasyCron** | Free tier | 2 min | ⭐⭐⭐ | Any |

---

## 🚀 **Recommended Setup by Platform:**

### **Heroku:**
```bash
# Use built-in scheduler
echo "ENABLE_CONTINUOUS_LEARNING=true" >> .env
git push heroku main

# OR use Heroku Scheduler add-on
heroku addons:create scheduler:standard
```

### **Railway:**
```bash
# Add environment variable
railway variables set ENABLE_CONTINUOUS_LEARNING=true

# Deploy
railway up
```

### **AWS/Google Cloud:**
```bash
# Use built-in scheduler for simplicity
ENABLE_CONTINUOUS_LEARNING=true
```

### **DigitalOcean/VPS:**
```bash
# Use system cron
crontab -e
# Add: 0 2 * * * cd /path/to/app && python3 scheduled_training.py
```

---

## ⚙️ Configuration

### **Environment Variables:**

Add to your `.env` or platform settings:

```bash
# Enable/disable continuous learning
ENABLE_CONTINUOUS_LEARNING=true

# API keys (required for training)
GOOGLE_SAFE_BROWSING_KEY=your_key
VIRUSTOTAL_API_KEY=your_key

# Optional: Training secret for webhook endpoints
TRAINING_SECRET=random_secret_here
```

---

## 🔍 Monitoring

### **Check if scheduler is running:**

```python
# In Flask shell or route
from background_scheduler import get_scheduler

scheduler = get_scheduler()
if scheduler:
    next_run = scheduler.get_next_run_time()
    print(f"Next training: {next_run}")
```

### **View logs:**

- **Heroku:** `heroku logs --tail | grep training`
- **Railway:** Check deployment logs
- **AWS:** CloudWatch logs
- **Local:** Check `training_schedule.log`

---

## 🎯 **Quick Start (Any Platform):**

1. **Add to `.env`:**
   ```bash
   ENABLE_CONTINUOUS_LEARNING=true
   ```

2. **Install dependency:**
   ```bash
   pip install APScheduler==3.10.4
   pip freeze > requirements.txt
   ```

3. **Commit and deploy:**
   ```bash
   git add .
   git commit -m "Enable continuous learning"
   git push
   ```

4. **Done!** Training runs daily at 2 AM UTC ✅

---

## 💡 **Tips:**

1. **Choose 2 AM UTC** - Low traffic time globally
2. **Monitor first week** - Ensure training completes successfully
3. **Check logs daily** - Catch any issues early
4. **Backup strategy** - Models auto-backup before training
5. **API limits** - Built-in rate limiting handles this

---

## ✅ **Recommended: Built-in Scheduler**

For most users, the **built-in background scheduler** is the easiest:

```bash
# Just add this to .env:
ENABLE_CONTINUOUS_LEARNING=true

# And deploy!
```

✨ **No additional setup, works everywhere, completely free!** ✨

---

## 🆘 Troubleshooting

### "Scheduler not running"
- Check: `ENABLE_CONTINUOUS_LEARNING=true` in environment
- Check: APScheduler installed
- Check: App logs for errors

### "Training fails"
- Check: API keys are set
- Check: PhishTank cache exists
- Check: Sufficient memory (>512MB)

### "Wrong timezone"
- Scheduler uses UTC by default
- Adjust in `background_scheduler.py`: `CronTrigger(hour=2)`

---

**You're all set for continuous learning in production!** 🚀

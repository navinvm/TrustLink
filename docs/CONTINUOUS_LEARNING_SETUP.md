# 🤖 Continuous Learning System - Setup Guide

## Overview

TrustLink now features **automatic daily retraining** that continuously improves the model with:
- ✅ Fresh PhishTank phishing URLs (updated daily)
- ✅ New safe URLs from 80+ legitimate domains
- ✅ User feedback from the database
- ✅ Triple verification from Google Safe Browsing + VirusTotal
- ✅ Runs every 24 hours automatically

## 🎯 What Gets Collected Daily

### 1. **Fresh Phishing URLs** (500/day)
- Downloaded from PhishTank's live database
- New phishing attempts from the past 24 hours
- Verified by community

### 2. **Updated Safe URLs** (300/day)
- Generated from 80+ legitimate domains
- Includes: Tech giants, social media, developer platforms, news sites, e-commerce, financial services
- Rotated daily for variety

### 3. **User Feedback**
- Collected from your database
- Real-world corrections from users
- High-quality labeled data

### 4. **Triple Verification**
- Each URL validated by all 3 APIs
- Consensus required (2 out of 3 must agree)
- Highest quality training data

## 📅 Automated Scheduling

### **Windows (Task Scheduler)**

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Click OK

2. **Create New Task**
   - Click "Create Basic Task"
   - Name: `TrustLink Daily Training`
   - Description: `Automatic model retraining with fresh data`

3. **Set Trigger**
   - When: Daily
   - Time: 2:00 AM (low traffic time)
   - Recur every: 1 day

4. **Set Action**
   - Action: Start a program
   - Program/script: `C:\path\to\schedule_daily_training.bat`
   - Start in: `C:\path\to\trustlink`

5. **Finish**
   - Click "Open Properties" when done
   - Check "Run whether user is logged on or not"
   - Check "Run with highest privileges"

### **Linux/Mac (Cron)**

1. **Edit crontab**
   ```bash
   crontab -e
   ```

2. **Add daily job** (runs at 2 AM)
   ```bash
   0 2 * * * cd /path/to/trustlink && /usr/bin/python3 scheduled_training.py >> training_cron.log 2>&1
   ```

3. **Save and exit**

### **Alternative: Python Scheduler (APScheduler)**

Add to `app.py` for in-process scheduling:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from scheduled_training import ContinuousLearningSystem

def run_scheduled_training():
    system = ContinuousLearningSystem()
    should_train, reason = system.should_train_today()
    if should_train:
        system.run_daily_training(phishing_limit=500, safe_limit=100)

# Start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_scheduled_training, 'cron', hour=2, minute=0)
scheduler.start()
```

## 🚀 Manual Run

Test the system manually:

```bash
python scheduled_training.py
```

## 📊 What Happens During Training

```
Day 1 (First Run):
  - Collect 500 phishing URLs from PhishTank
  - Generate 300 safe URLs
  - Collect user feedback (if any)
  - Triple-verify all URLs (2/3 APIs must agree)
  - Train model with ~800 samples
  - Save new model and metrics
  - Update accuracy display

Day 2 (Next Day):
  - Check: Has 24 hours passed? ✓
  - Collect 500 NEW phishing URLs
  - Generate 300 NEW safe URLs (different pages/domains)
  - Collect NEW user feedback
  - Triple-verify everything
  - Retrain with NEW + OLD data
  - Model gets smarter!

Day 3, 4, 5... (Continuous):
  - Model keeps learning from fresh threats
  - Adapts to new phishing techniques
  - Incorporates user corrections
  - Accuracy improves over time
```

## 📁 Files Created

- **`phishtank_cache.json`** - Cached PhishTank data (24hr lifespan)
- **`last_training.json`** - Timestamp of last training
- **`training_history.json`** - Last 30 days of training metrics
- **`training_schedule.log`** - Execution log

## 🔍 Monitoring

### Check Last Training

```python
import json
with open('last_training.json', 'r') as f:
    data = json.load(f)
    print(f"Last training: {data['timestamp']}")
    print(f"Samples: {data['samples']}")
    print(f"Accuracy: {data['accuracy']:.2%}")
```

### View Training History

```python
import json
with open('training_history.json', 'r') as f:
    history = json.load(f)
    for entry in history[-5:]:  # Last 5 trainings
        print(f"{entry['timestamp']}: {entry['accuracy']:.2%} ({entry['samples']} samples)")
```

### Check Model Metrics

The `model_metrics.json` file is automatically updated after each training:

```json
{
    "accuracy": 0.978,
    "precision": 0.981,
    "recall": 0.975,
    "training_samples": 2414,
    "last_updated": "2026-02-09T02:00:00",
    "model_version": "2.0",
    "data_sources": ["PhishTank", "Safe Domains", "User Feedback"],
    "training_type": "continuous_daily"
}
```

## ⚙️ Configuration

Edit `scheduled_training.py` to adjust:

```python
# In run_daily_training() method:
phishing_limit=500,   # Phishing URLs per day
safe_limit=100        # Safe domains per day (300 URLs)
```

### Recommended Settings:

| Environment | Phishing | Safe | Frequency |
|-------------|----------|------|-----------|
| Development | 100 | 30 | Manual only |
| Staging | 300 | 75 | Daily |
| Production | 500 | 100 | Daily |
| High Traffic | 1000 | 200 | Every 12 hours |

## 🎯 Expected Results

### Week 1
- **Day 1**: Baseline model (2600 samples, ~96% accuracy)
- **Day 7**: +3500 samples, ~97% accuracy

### Month 1
- **Day 30**: +15,000 samples, ~98% accuracy
- Model adapts to current phishing trends
- Better detection of new attack patterns

### Long Term
- Continuous improvement
- Always up-to-date with latest threats
- Learns from real user feedback
- Professional-grade accuracy

## 🛠️ Troubleshooting

### "Not enough training data collected"
- **Cause**: PhishTank rate limit or API errors
- **Solution**: Wait a few hours, data will be cached
- **Prevention**: Uses cache for 24 hours automatically

### "Training skipped - will check again in 24 hours"
- **Cause**: Last training was < 24 hours ago
- **Solution**: This is normal, wait for next scheduled run
- **Override**: Delete `last_training.json` to force run

### API Rate Limits
- **PhishTank**: Cached for 24 hours (rarely hits limit)
- **Google**: 10,000 queries/day (plenty for 800 URLs)
- **VirusTotal**: 4/minute (handled by batch delays)

### Training Takes Too Long
- **Normal**: 15-20 minutes for 800 URLs
- **If longer**: Check internet connection
- **Solution**: Reduce `phishing_limit` and `safe_limit`

## 📈 Performance Impact

- **CPU**: Moderate during training (15-20 min)
- **Memory**: ~500MB during training
- **Network**: ~50MB download (PhishTank + API calls)
- **Disk**: ~5MB per day (cached data)

**Recommended**: Schedule during low-traffic hours (2-4 AM)

## ✅ Best Practices

1. **Monitor regularly** - Check training logs weekly
2. **Review accuracy trends** - Watch training_history.json
3. **Backup models** - Script auto-backups before training
4. **Test after updates** - Scan known URLs to verify
5. **Clear old cache** - Delete phishtank_cache.json if stale

## 🎉 Summary

Your TrustLink model now:
- ✅ **Learns continuously** from new threats
- ✅ **Adapts automatically** to phishing trends
- ✅ **Improves daily** with fresh data
- ✅ **Incorporates feedback** from real users
- ✅ **Triple-verifies** everything for quality
- ✅ **Runs automatically** every 24 hours

**Set it and forget it!** 🚀

Your model will keep getting smarter every single day without any manual intervention.

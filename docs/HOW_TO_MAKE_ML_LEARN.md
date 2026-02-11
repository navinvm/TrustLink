# 🎓 How to Make TrustLink's Machine Learning Learn

## Overview
TrustLink has a **complete learning system** built-in, but it needs three things to work:
1. **API Keys** for external threat intelligence
2. **User Feedback** to identify mistakes
3. **Periodic Retraining** to incorporate new knowledge

---

## 🔑 Step 1: Get API Keys (External Threat Intelligence)

### Why You Need This
The ML model learns by comparing its predictions against **verified threat intelligence sources**:
- **Google Safe Browsing** - Google's massive threat database
- **VirusTotal** - Aggregates 70+ antivirus engines
- **PhishTank** - Community-driven phishing database (FREE!)

### How to Get API Keys

#### 1. Google Safe Browsing API (Recommended)
```
1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable "Safe Browsing API"
4. Create credentials → API Key
5. Copy your API key
```
**Cost:** FREE (10,000 requests/day)

#### 2. VirusTotal API
```
1. Go to: https://www.virustotal.com/gui/join-us
2. Create a free account
3. Go to your profile → API Key
4. Copy your API key
```
**Cost:** FREE (4 requests/minute, 500/day)

#### 3. PhishTank (No key needed!)
```
PhishTank works without an API key - it's already enabled!
```

### How to Add API Keys to TrustLink

#### Option A: Environment Variables (Recommended)
```bash
# Windows (PowerShell)
$env:GOOGLE_SAFE_BROWSING_KEY = "your-google-api-key-here"
$env:VIRUSTOTAL_API_KEY = "your-virustotal-api-key-here"

# Linux/Mac (Bash)
export GOOGLE_SAFE_BROWSING_KEY="your-google-api-key-here"
export VIRUSTOTAL_API_KEY="your-virustotal-api-key-here"
```

#### Option B: Modify app.py
Edit `app.py` around line 48:
```python
validator_config = {
    'google_api_key': 'YOUR-GOOGLE-KEY-HERE',
    'virustotal_api_key': 'YOUR-VIRUSTOTAL-KEY-HERE',
}
```

---

## 👤 Step 2: Collect User Feedback

### What is User Feedback?
When the ML model makes a mistake, users can report it:
- **False Positive**: Marked legitimate site as phishing
- **False Negative**: Missed an actual phishing site

### How It Works (Already Built-In!)

#### Frontend Integration Needed
Add a feedback button to your scan results page:

```javascript
// In static/js/main.js or templates/index.html
function submitFeedback(scanId, url, originalPrediction, correctLabel) {
    fetch('/api/v1/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            scan_id: scanId,
            url: url,
            original_prediction: originalPrediction,
            correct_label: correctLabel,  // 'Safe' or 'Phishing'
            feedback_type: 'user_report'
        })
    })
    .then(response => response.json())
    .then(data => {
        alert('Thank you for your feedback! This will help improve the model.');
    });
}
```

#### Example UI Addition
```html
<!-- Add to scan results -->
<div class="feedback-section">
    <p>Was this prediction correct?</p>
    <button onclick="submitFeedback(scanId, url, 'Phishing', 'Safe')">
        ❌ No, this is actually SAFE
    </button>
    <button onclick="submitFeedback(scanId, url, 'Safe', 'Phishing')">
        ❌ No, this is actually PHISHING
    </button>
    <button>✅ Yes, prediction is correct</button>
</div>
```

---

## 🔄 Step 3: Retrain the Model

### Automatic Learning Process

#### A. External Validation (Automatic)
When you have API keys, TrustLink automatically:
1. Checks URLs against threat intelligence APIs
2. Stores high-confidence results (>80%) as training data
3. Uses consensus from multiple sources

#### B. Manual Retraining
Trigger retraining when you have enough new data:

```bash
# Using API
curl -X POST http://localhost:5000/api/v1/retrain \
  -H "X-API-Key: YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "min_confidence": 0.7,
    "verified_only": false
  }'
```

```python
# Or programmatically
import requests

response = requests.post(
    'http://localhost:5000/api/v1/retrain',
    headers={'X-API-Key': 'your-api-key'},
    json={'min_confidence': 0.7, 'verified_only': False}
)

print(response.json())
# Output: {
#   'status': 'success',
#   'message': 'Model retrained successfully',
#   'version': 'v2.20260205_142530',
#   'metrics': {
#     'accuracy': 0.94,
#     'precision': 0.92,
#     'recall': 0.89
#   },
#   'training_samples': 1523
# }
```

### When to Retrain
- **Weekly**: If you have active users providing feedback
- **Monthly**: For moderate usage
- **On-demand**: When you notice accuracy issues

### Check Training Data Status
```bash
curl -X GET http://localhost:5000/api/v1/training-stats \
  -H "X-API-Key: YOUR-API-KEY"
```

Output:
```json
{
  "status": "success",
  "total_available": 1523,
  "pending_feedback": 45,
  "by_source": [
    {
      "source": "external_api",
      "count": 1200,
      "avg_confidence": 0.92,
      "phishing_count": 450,
      "safe_count": 750
    },
    {
      "source": "user_feedback",
      "count": 323,
      "avg_confidence": 0.9,
      "phishing_count": 100,
      "safe_count": 223
    }
  ]
}
```

---

## 🎯 Complete Learning Workflow

### Day-to-Day Operation

```
1. USER scans URL
   ↓
2. ML MODEL predicts + External APIs verify (if API keys present)
   ↓
3. If APIs agree & high confidence → Auto-added to training data ✅
   ↓
4. USER sees result
   ↓
5. If USER disagrees → Submits feedback → Added to training data ✅
   ↓
6. ADMIN reviews training data weekly
   ↓
7. ADMIN triggers retrain → New improved model! 🎉
   ↓
8. Repeat - Model gets smarter over time!
```

---

## 📊 Monitoring Model Performance

### View Model History
```bash
curl -X GET http://localhost:5000/api/v1/model-history \
  -H "X-API-Key: YOUR-API-KEY"
```

### What You'll See
```json
{
  "status": "success",
  "history": [
    {
      "version": "v2.20260205_142530",
      "accuracy": 0.94,
      "precision": 0.92,
      "recall": 0.89,
      "training_samples": 1523,
      "created_at": "2026-02-05T14:25:30"
    },
    {
      "version": "v2.20260129_103045",
      "accuracy": 0.91,
      "precision": 0.88,
      "recall": 0.85,
      "training_samples": 1200,
      "created_at": "2026-01-29T10:30:45"
    }
  ]
}
```

---

## 🚀 Quick Start Checklist

### Minimum Setup (Free!)
- [ ] Use PhishTank (already enabled, no key needed)
- [ ] Add feedback buttons to your UI
- [ ] Retrain monthly with accumulated feedback

### Recommended Setup
- [ ] Get Google Safe Browsing API key (FREE)
- [ ] Get VirusTotal API key (FREE tier)
- [ ] Add environment variables
- [ ] Add feedback UI
- [ ] Set up weekly retraining schedule

### Advanced Setup
- [ ] Automate retraining (cron job/scheduled task)
- [ ] Monitor model metrics dashboard
- [ ] A/B test model versions
- [ ] Custom whitelist management

---

## 💡 Key Insights

### What Makes the Model Learn?
1. **Quantity**: More diverse training examples
2. **Quality**: High-confidence verified data
3. **Balance**: Equal mix of phishing and safe URLs
4. **Freshness**: Recent phishing campaigns

### Current Model Status
- **Trained on**: ~5000 URLs from public datasets
- **Accuracy**: ~92% (baseline)
- **Needs**: Real-world data from YOUR users!

### Why External APIs Matter
- **Verified Ground Truth**: Known bad URLs from multiple sources
- **Up-to-date**: Latest phishing campaigns
- **High Confidence**: Multiple engines agreeing = reliable training data

---

## 🎓 Learning System Architecture

```
┌─────────────────────────────────────────────────┐
│              USER SCANS URL                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           ML MODEL PREDICTION                    │
│  • RandomForest Classifier                       │
│  • TF-IDF Vectorization                         │
│  • Character n-grams (1-3)                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      EXTERNAL VALIDATION (if API keys)           │
│  • Google Safe Browsing                          │
│  • VirusTotal (70+ engines)                      │
│  • PhishTank (community)                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        CONSENSUS & CONFIDENCE                    │
│  • Weighted voting                               │
│  • Agreement bonus                               │
│  • Store high-confidence (>80%)                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           TRAINING DATA DB                       │
│  • Verified URLs with labels                     │
│  • Confidence scores                             │
│  • Source tracking                               │
│  • User feedback                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        PERIODIC RETRAINING                       │
│  • Combines old + new data                       │
│  • Evaluates metrics                             │
│  • Saves improved model                          │
│  • Versions tracked                              │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### "Learning system not available"
**Problem**: External APIs not loaded  
**Solution**: Add API keys and restart Flask

### "Not enough training data"
**Problem**: < 10 samples for retraining  
**Solution**: Collect more feedback or lower `min_confidence`

### "Model performance not improving"
**Problem**: Low-quality training data  
**Solutions**:
- Increase `min_confidence` to 0.8+
- Use `verified_only=True`
- Get more diverse URLs

---

## 📚 Additional Resources

- **API Guide**: See `API_GUIDE.md` for all endpoints
- **Learning Details**: See `ML_LEARNING_GUIDE.md` for deep dive
- **Database Schema**: See `database.py` for training data tables

---

## ❓ FAQ

**Q: Can it learn without API keys?**  
A: Yes, through user feedback only (slower but works!)

**Q: How much does it cost?**  
A: FREE! All recommended APIs have free tiers sufficient for most use cases.

**Q: How often should I retrain?**  
A: Weekly if active, monthly otherwise, or when you notice issues.

**Q: Will retraining break the model?**  
A: No! Old versions are tracked, you can always roll back.

**Q: How do I know it's learning?**  
A: Check model history - accuracy/precision/recall should improve over time.

---

## 🎉 Summary

### TrustLink ALREADY HAS:
✅ Complete learning infrastructure  
✅ External API integration  
✅ Training data storage  
✅ Model retraining system  
✅ Feedback collection  
✅ Version tracking  

### YOU NEED TO ADD:
1. **API keys** (5 minutes, FREE)
2. **Feedback UI** (copy-paste HTML/JS)
3. **Retrain weekly** (one API call)

That's it! The system will learn and improve automatically! 🚀

# 🎓 How TrustLink's ML Model Learns From Malicious Phishing

## The Problem You Asked About

**Question:** "How would it learn if the phishing is malicious?"

**Answer:** The model now has **three learning mechanisms** to continuously improve its phishing detection:

---

## 🔄 Learning Mechanism #1: External API Validation

### How It Works

When a URL is scanned, TrustLink can automatically validate it against **real-world threat intelligence databases**:

1. **Google Safe Browsing** - Google's massive threat database (updated hourly)
2. **VirusTotal** - Aggregates 70+ antivirus engines and security vendors
3. **PhishTank** - Community-verified phishing database

### The Learning Process

```
User scans URL → TrustLink predicts → External APIs validate → Add to training data
```

**Example:**
```
URL: http://paypal-verify.tk/login
TrustLink says: "Safe" (60% confidence)
Google says: "PHISHING" (95% confidence)
VirusTotal says: "MALICIOUS" (89% confidence)
PhishTank says: "VERIFIED PHISHING"

Result: TrustLink learns this is actually PHISHING
→ Added to training_data table with label=1 (phishing)
```

### Code Example

```python
# Validate a URL and automatically learn from it
response = requests.post(
    "http://localhost:5000/api/v1/validate-external",
    json={"url": "http://suspicious-site.com"},
    headers={"X-API-Key": "your_api_key"}
)

# If high confidence, automatically added to training data
# Next retraining cycle will include this example
```

---

## 🙋 Learning Mechanism #2: User Feedback

### How It Works

Users can report when TrustLink makes a mistake:

- **False Positive**: TrustLink said "Phishing" but it's actually safe
- **False Negative**: TrustLink said "Safe" but it's actually phishing

### The Learning Process

```
User reports error → Feedback stored → Added to training data → Model learns
```

**Example:**
```
User scans: http://legitimate-bank.com
TrustLink says: "Phishing" (70% confidence) ❌ WRONG!
User clicks: "Report False Positive"

Result: TrustLink learns this is actually SAFE
→ Added to training_data with label=0 (safe)
```

### Code Example

```python
# Submit feedback about incorrect prediction
response = requests.post(
    "http://localhost:5000/api/v1/feedback",
    json={
        "url": "http://legitimate-site.com",
        "original_prediction": "Phishing",
        "correct_label": "Safe",
        "feedback_type": "false_positive"
    }
)
```

---

## 🔁 Learning Mechanism #3: Model Retraining

### How It Works

Accumulated training data is used to retrain the machine learning model:

1. **Collect** verified examples from external APIs and user feedback
2. **Filter** high-confidence data (>70% confidence by default)
3. **Retrain** the Random Forest model with new examples
4. **Evaluate** performance (accuracy, precision, recall)
5. **Deploy** new model version if improved

### The Learning Process

```
Training data accumulates → Trigger retrain → Model updates → Better predictions
```

**Example:**

```
Week 1: Model trained on 1,000 URLs (80% accuracy)
↓
Week 2: Collected 150 new verified URLs
        - 100 from external APIs (high confidence)
        - 50 from user feedback
↓
Trigger retraining
↓
Week 3: Model v2 trained on 1,150 URLs (85% accuracy) ✅
```

### Code Example

```python
# Check available training data
stats = requests.get(
    "http://localhost:5000/api/v1/training-stats",
    headers={"X-API-Key": "your_api_key"}
).json()

print(f"Available: {stats['total_available']} samples")

# Retrain when enough data collected
if stats['total_available'] >= 50:
    retrain = requests.post(
        "http://localhost:5000/api/v1/retrain",
        json={"min_confidence": 0.8, "verified_only": False},
        headers={"X-API-Key": "your_api_key"}
    ).json()
    
    print(f"New version: {retrain['version']}")
    print(f"Accuracy: {retrain['metrics']['accuracy']}")
```

---

## 📊 Complete Learning Workflow

### Real-World Scenario

Let's say a new phishing campaign starts using domain: `amaz0n-security.tk`

#### Day 1: Initial Detection
```
1. User scans: http://amaz0n-security.tk/verify-account
2. TrustLink (old model): "Safe" (55% confidence) ❌
3. External validation triggered:
   - Google: "SOCIAL_ENGINEERING"
   - VirusTotal: 35/70 engines flag as malicious
   - PhishTank: Not yet in database
4. Consensus: PHISHING (90% confidence)
5. ✅ Added to training_data table
```

#### Day 2: More Reports
```
1. 10 more users scan the same domain
2. 5 users report: "This is phishing!" (feedback)
3. ✅ 5 more entries added to training_data
```

#### Day 3: Retraining
```
1. System has collected 15 verified examples of this phishing site
2. Admin triggers retraining:
   POST /api/v1/retrain
3. Model learns the pattern:
   - Suspicious TLD (.tk)
   - Brand impersonation (amaz0n vs amazon)
   - Security keywords
4. ✅ New model version deployed
```

#### Day 4: Improved Detection
```
1. New user scans: http://appl3-security.tk/login
2. TrustLink (new model): "Phishing" (92% confidence) ✅
3. Model learned the pattern and detects similar threats!
```

---

## 🎯 Key Features

### 1. Automatic Data Collection
- External APIs automatically validate URLs
- High-confidence results added to training pool
- No manual labeling required

### 2. Quality Control
- Only high-confidence data used (>70% by default)
- Multiple sources must agree (consensus voting)
- Verified vs. unverified data tracking

### 3. Version Control
- Every retraining creates a new version
- Performance metrics tracked
- Can rollback if needed

### 4. Continuous Improvement
```
More scans → More validation → More data → Better model → More scans...
```

---

## 📈 Performance Tracking

### Database Tables

**training_data**
```sql
SELECT source, COUNT(*) as count FROM training_data GROUP BY source;

| source        | count |
|---------------|-------|
| external_api  | 250   |
| user_feedback | 50    |
```

**model_versions**
```sql
SELECT version, accuracy, training_samples FROM model_versions;

| version            | accuracy | samples |
|--------------------|----------|---------|
| v2.20260205_120000 | 0.80     | 1000    |
| v2.20260210_140000 | 0.85     | 1150    |
| v2.20260215_160000 | 0.89     | 1400    |
```

---

## 🚀 Getting Started

### Step 1: Enable External Validation (Optional)

Set up API keys for automatic threat intelligence:

```bash
# Get API keys (see LEARNING_SYSTEM.md for details)
export GOOGLE_SAFE_BROWSING_KEY="your_key"
export VIRUSTOTAL_API_KEY="your_key"

# Restart TrustLink
python app.py
```

### Step 2: Use the System

Scans automatically contribute to learning:
```python
# Regular scan
response = requests.post(
    "http://localhost:5000/predict",
    json={"url": "http://suspicious-site.com"}
)

# System can automatically validate and learn in background
```

### Step 3: Trigger Retraining

Once enough data collected:
```python
# Check available data
GET /api/v1/training-stats

# Retrain model
POST /api/v1/retrain

# Check improvement
GET /api/v1/model-history
```

---

## 💡 Benefits of This Approach

✅ **Real-World Learning** - Uses actual threat intelligence, not synthetic data  
✅ **Continuous Improvement** - Model gets better over time automatically  
✅ **Community-Driven** - User feedback helps everyone  
✅ **Zero-Day Detection** - Can learn about new threats within hours  
✅ **Verified Data** - Multiple sources validate each threat  
✅ **Automated Pipeline** - Minimal manual intervention needed  

---

## 🔒 Security Considerations

1. **API Keys** - Stored in environment variables, never in code
2. **Rate Limiting** - Respects API rate limits (caching used)
3. **Data Privacy** - URLs validated, but no user data sent
4. **Confidence Thresholds** - Only high-quality data used for training
5. **Version Control** - Can audit and rollback model changes

---

## 📚 Related Documentation

- **LEARNING_SYSTEM.md** - Detailed API documentation
- **API_GUIDE.md** - General API usage
- **README.md** - Application overview

---

## Summary: Answering Your Question

**"How would it learn if the phishing is malicious?"**

1. **External APIs** validate URLs against known threat databases
2. **Users report** incorrect predictions (false positives/negatives)
3. **Training data** accumulates with verified labels
4. **Model retrains** periodically with new examples
5. **Better predictions** for future similar threats

The system creates a **continuous learning loop** where each scan contributes to improving the model for everyone! 🎓

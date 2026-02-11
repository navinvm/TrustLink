# 🧠 TrustLink Learning System

## Overview

TrustLink now includes an advanced **Machine Learning Enhancement System** that enables the model to learn from new threats and improve over time. The system validates URLs against external threat intelligence sources and uses this data to continuously retrain the model.

## How It Works

### 1. **External Validation** 🔍

The system can validate URLs against multiple threat intelligence sources:

- **Google Safe Browsing API** - Checks against Google's threat database
- **VirusTotal API** - Aggregates results from 70+ antivirus engines
- **PhishTank** - Free community-driven phishing database (no API key needed)

### 2. **Data Collection** 📊

Training data is collected from multiple sources:

- **External API Validation**: High-confidence labels from threat intelligence
- **User Feedback**: Reports of false positives/negatives
- **Scan History**: Predictions with confidence scores

### 3. **Model Retraining** 🔄

The model can be retrained with accumulated data:

- Minimum 10 samples required
- Uses verified and high-confidence data
- Preserves model performance metrics
- Tracks version history

## Setup Instructions

### Step 1: Obtain API Keys (Optional but Recommended)

#### Google Safe Browsing API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Safe Browsing API"
4. Create credentials (API Key)
5. Copy your API key

#### VirusTotal API
1. Sign up at [VirusTotal](https://www.virustotal.com/gui/join-us)
2. Go to your profile settings
3. Copy your API key

### Step 2: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:GOOGLE_SAFE_BROWSING_KEY = "your_google_key_here"
$env:VIRUSTOTAL_API_KEY = "your_virustotal_key_here"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_SAFE_BROWSING_KEY=your_google_key_here
set VIRUSTOTAL_API_KEY=your_virustotal_key_here
```

**Linux/Mac:**
```bash
export GOOGLE_SAFE_BROWSING_KEY="your_google_key_here"
export VIRUSTOTAL_API_KEY="your_virustotal_key_here"
```

### Step 3: Restart TrustLink

```bash
python app.py
```

You should see:
```
✓ Learning system enabled
```

## API Endpoints

### 1. External Validation

**Endpoint:** `POST /api/v1/validate-external`

**Headers:** `X-API-Key: your_api_key`

**Request:**
```json
{
  "url": "http://suspicious-site.com"
}
```

**Response:**
```json
{
  "status": "success",
  "url": "http://suspicious-site.com",
  "validation": {
    "is_threat": true,
    "confidence": 0.92,
    "consensus": "threat",
    "threat_votes": 2,
    "safe_votes": 0,
    "sources": [...]
  },
  "cached": false
}
```

### 2. Submit Feedback

**Endpoint:** `POST /api/v1/feedback`

**Authentication:** Login required (session-based)

**Request:**
```json
{
  "scan_id": 123,
  "url": "http://example.com",
  "original_prediction": "Safe",
  "correct_label": "Phishing",
  "feedback_type": "false_negative"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Thank you for your feedback!",
  "feedback_id": 45
}
```

### 3. Retrain Model

**Endpoint:** `POST /api/v1/retrain`

**Headers:** `X-API-Key: your_api_key`

**Request:**
```json
{
  "min_confidence": 0.7,
  "verified_only": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Model retrained successfully",
  "version": "v2.20260205_143022",
  "metrics": {
    "accuracy": 0.85,
    "new_samples": 150
  },
  "training_samples": 150
}
```

### 4. Training Statistics

**Endpoint:** `GET /api/v1/training-stats`

**Headers:** `X-API-Key: your_api_key`

**Response:**
```json
{
  "status": "success",
  "total_available": 150,
  "pending_feedback": 5,
  "by_source": [
    {
      "source": "external_api",
      "count": 100,
      "avg_confidence": 0.92,
      "phishing_count": 75,
      "safe_count": 25
    },
    {
      "source": "user_feedback",
      "count": 50,
      "avg_confidence": 0.9,
      "phishing_count": 30,
      "safe_count": 20
    }
  ]
}
```

### 5. Model History

**Endpoint:** `GET /api/v1/model-history`

**Headers:** `X-API-Key: your_api_key`

**Response:**
```json
{
  "status": "success",
  "history": [
    {
      "id": 1,
      "version": "v2.20260205_143022",
      "accuracy": 0.85,
      "precision_score": 0.87,
      "recall_score": 0.83,
      "training_samples": 150,
      "trained_at": "2026-02-05T14:30:22",
      "is_active": 1,
      "notes": "Retrained with 150 samples"
    }
  ]
}
```

## Usage Examples

### Python Example: Validate and Learn

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "http://localhost:5000"

headers = {"X-API-Key": API_KEY}

# Validate a suspicious URL
response = requests.post(
    f"{BASE_URL}/api/v1/validate-external",
    json={"url": "http://paypal-verify.tk/login"},
    headers={**headers, "Content-Type": "application/json"}
)

result = response.json()
print(f"Threat: {result['validation']['is_threat']}")
print(f"Confidence: {result['validation']['confidence']}")

# Check training stats
stats = requests.get(
    f"{BASE_URL}/api/v1/training-stats",
    headers=headers
).json()

print(f"Available training samples: {stats['total_available']}")

# Retrain if enough data
if stats['total_available'] >= 50:
    retrain = requests.post(
        f"{BASE_URL}/api/v1/retrain",
        json={"min_confidence": 0.8},
        headers={**headers, "Content-Type": "application/json"}
    ).json()
    
    print(f"Model retrained: {retrain['version']}")
    print(f"Accuracy: {retrain['metrics']['accuracy']}")
```

## Database Schema

### New Tables

**feedback** - User corrections and reports
```sql
id, scan_id, user_id, url, original_prediction, correct_label,
feedback_type, created_at, is_processed
```

**external_validations** - Cached validation results
```sql
id, url, url_hash, is_threat, confidence, source, threat_type,
validated_at, metadata
```

**training_data** - Training data pool
```sql
id, url, label, confidence, source, added_at,
used_in_training, verified
```

**model_versions** - Training history
```sql
id, version, accuracy, precision_score, recall_score,
training_samples, trained_at, is_active, notes
```

## Benefits

✅ **Continuous Learning** - Model improves over time with new threats  
✅ **External Validation** - Leverages industry-leading threat intelligence  
✅ **User Feedback** - Community-driven accuracy improvements  
✅ **Version Control** - Track model performance over time  
✅ **Automated Pipeline** - Collect, validate, and retrain automatically  

## Security Notes

- API keys are read from environment variables (never hardcoded)
- External validation results are cached (24-hour TTL)
- Only high-confidence data used for training (threshold: 0.7+)
- Model versions are tracked for rollback capability
- Admin API key required for retraining

## Troubleshooting

**Issue:** Learning system shows as disabled

**Solution:** 
1. Check if API keys are set in environment
2. Verify `ml_learning.py` file exists
3. Check console for import errors

**Issue:** External validation fails

**Solution:**
1. Verify API keys are valid
2. Check API rate limits
3. Test with PhishTank (no key required)

**Issue:** Not enough training data

**Solution:**
1. Run more scans to collect data
2. Validate URLs against external APIs
3. Submit user feedback
4. Lower `min_confidence` threshold

## Free Tier Limits

- **Google Safe Browsing**: 10,000 requests/day (free)
- **VirusTotal**: 4 requests/minute (free tier)
- **PhishTank**: Unlimited (free, no key needed)

## Future Enhancements

- [ ] Automated scheduled retraining
- [ ] Active learning (model requests validation for uncertain cases)
- [ ] Ensemble models with voting
- [ ] Real-time online learning
- [ ] Integration with more threat intelligence sources

---

**Note:** The system works without API keys but with limited learning capability (user feedback only).

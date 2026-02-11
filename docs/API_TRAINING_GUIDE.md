# 🧠 API-Based Model Training Guide

TrustLink can now train its ML model using real-world data from external threat intelligence APIs!

## 🎯 Overview

Instead of using static training data, TrustLink can now:
- **Collect verified phishing URLs** from PhishTank's live database
- **Generate safe URL samples** from known legitimate domains
- **Validate URLs** using Google Safe Browsing and VirusTotal
- **Automatically retrain** the model with fresh data
- **Update accuracy metrics** in real-time

## 📊 Data Sources

### 1. **PhishTank** (Free, No API Key Required)
- Provides verified phishing URLs
- Community-verified database
- Updated in real-time
- URL: http://data.phishtank.com/

### 2. **Google Safe Browsing** (Optional)
- Additional threat validation
- Requires API key
- Get key: https://developers.google.com/safe-browsing

### 3. **VirusTotal** (Optional)
- Multi-engine URL scanning
- Requires API key
- Get key: https://www.virustotal.com/gui/join-us

## 🚀 Quick Start

### Basic Training (PhishTank Only)

```bash
python train_from_apis.py
```

This will:
1. Collect 500 verified phishing URLs from PhishTank
2. Generate 300 safe URLs from 100 legitimate domains
3. Train the model with ~800 total samples
4. Save the new model and update metrics

### Advanced Training (With All APIs)

```bash
# Set API keys as environment variables
export GOOGLE_SAFE_BROWSING_KEY="your_google_key"
export VIRUSTOTAL_API_KEY="your_virustotal_key"

# Run training
python train_from_apis.py
```

## 💻 Programmatic Usage

### Train from Python Code

```python
from ml_learning import train_model_from_apis

# Train with default settings (500 phishing, 100 safe domains)
metrics = train_model_from_apis()

# Train with custom settings
metrics = train_model_from_apis(
    api_config={
        'google_api_key': 'YOUR_GOOGLE_KEY',
        'virustotal_api_key': 'YOUR_VT_KEY'
    },
    phishing_limit=1000,  # Collect 1000 phishing URLs
    safe_limit=200        # Use 200 safe domains (600 URLs)
)

print(f"New model accuracy: {metrics['accuracy']:.2%}")
```

### Collect Custom Training Data

```python
from ml_learning import ExternalValidator, APIDataCollector

# Initialize
validator = ExternalValidator({
    'google_api_key': 'YOUR_KEY'
})
collector = APIDataCollector(validator)

# Collect phishing URLs
phishing_data = collector.collect_from_phishtank(limit=1000)

# Generate safe URLs
safe_data = collector.collect_safe_urls(['google.com', 'github.com'])

# Validate custom URLs
custom_urls = ['http://suspicious-site1.com', 'http://suspicious-site2.com']
validated = collector.validate_and_collect(custom_urls, min_confidence=0.8)
```

## 📈 Training Process

### Step-by-Step Breakdown

1. **Data Collection**
   ```
   📥 Collecting verified phishing URLs from PhishTank...
   ✓ Collected 500 verified phishing URLs
   
   📥 Generating safe URL samples...
   ✓ Generated 300 safe URL samples
   ```

2. **Dataset Summary**
   ```
   📊 Training Dataset Summary:
     Total samples: 800
     Phishing: 500 (62.5%)
     Safe: 300 (37.5%)
   ```

3. **Model Training**
   ```
   🧠 Training model with 800 samples...
   ✓ Model trained - Accuracy: 96.8%, Precision: 97.2%, Recall: 96.1%
   ```

4. **Save Results**
   ```
   💾 Saving trained model...
   ✓ Model saved to models/model.pkl
   
   💾 Saving model metrics...
   ✓ Metrics saved to model_metrics.json
   ```

## 🎛️ Configuration Options

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `phishing_limit` | 500 | Max phishing URLs to collect from PhishTank |
| `safe_limit` | 100 | Number of legitimate domains to use |
| `min_confidence` | 0.7 | Minimum confidence for API validation |

### API Configuration

```python
api_config = {
    'google_api_key': 'YOUR_GOOGLE_KEY',      # Optional
    'virustotal_api_key': 'YOUR_VT_KEY',      # Optional
    'phishtank_api_key': None                 # Not required (free)
}
```

## 📊 Model Metrics

After training, metrics are automatically saved to `model_metrics.json`:

```json
{
    "accuracy": 0.968,
    "precision": 0.972,
    "recall": 0.961,
    "training_samples": 800,
    "last_updated": "2026-02-09T03:00:00",
    "model_version": "2.0",
    "data_sources": ["PhishTank", "Legitimate Domains"]
}
```

These metrics automatically update the **accuracy display** across all pages!

## ⚠️ Important Notes

### Rate Limits
- **PhishTank**: No rate limit for database download
- **Google Safe Browsing**: 10,000 queries/day (free tier)
- **VirusTotal**: 4 requests/minute (free tier)

### Best Practices

1. **Backup First**: The script automatically backs up your current model
2. **Start Small**: Test with 100-200 samples first
3. **Increase Gradually**: Scale up as you verify performance
4. **Monitor Accuracy**: Check if new accuracy is better before using in production
5. **Schedule Regular Updates**: Retrain weekly/monthly with fresh data

### Data Quality

- PhishTank provides **verified** phishing URLs (high quality)
- Safe URLs are generated from **known legitimate** domains
- Optional API validation adds **extra verification**
- Model learns from **real-world threats**

## 🔄 Automated Training

### Set Up Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add weekly training (every Sunday at 2 AM)
0 2 * * 0 cd /path/to/trustlink && python train_from_apis.py
```

### Set Up Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., weekly)
4. Action: Run `python train_from_apis.py`
5. Set working directory to TrustLink folder

## 🐛 Troubleshooting

### "Not enough data collected"
- PhishTank API might be down
- Check internet connection
- Try reducing `phishing_limit`

### "API rate limit exceeded"
- Wait before retrying
- Reduce `phishing_limit` or `safe_limit`
- Use only PhishTank (no API key required)

### "Training failed"
- Check model backup in `models/` folder
- Verify Python dependencies: `sklearn`, `requests`, `numpy`
- Check disk space for model storage

## 📚 Further Reading

- [PhishTank API Documentation](https://www.phishtank.com/api_info.php)
- [Google Safe Browsing API](https://developers.google.com/safe-browsing)
- [VirusTotal API](https://developers.virustotal.com/reference)
- [Scikit-learn RandomForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)

## 💡 Example Output

```
╔════════════════════════════════════════════════════════════════╗
║          TrustLink - API-Based Model Training                  ║
╚════════════════════════════════════════════════════════════════╝

📡 Available APIs: PhishTank (Free)

======================================================================
🚀 TRAINING MODEL FROM EXTERNAL API DATA
======================================================================
📥 Collecting verified phishing URLs from PhishTank...
✓ Collected 500 verified phishing URLs
📥 Generating safe URL samples...
✓ Generated 300 safe URL samples

📊 Training Dataset Summary:
  Total samples: 800
  Phishing: 500 (62.5%)
  Safe: 300 (37.5%)

🧠 Training model with 800 samples...
✓ Model trained - Accuracy: 96.80%, Precision: 97.20%, Recall: 96.10%

💾 Saving trained model...
✓ Model saved to models/model.pkl
💾 Saving model metrics...

======================================================================
✅ MODEL TRAINING COMPLETE!
======================================================================
Accuracy: 96.80%
Precision: 97.20%
Recall: 96.10%
Training Samples: 800
======================================================================
```

---

**Ready to train your model with real-world data? Run `python train_from_apis.py` now!** 🚀

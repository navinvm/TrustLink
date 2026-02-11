# 🛡️ TrustLink: Phishing Detection System v2.0

**Advanced URL Threat Detection using Machine Learning & Pattern Recognition**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.0+-orange.svg)
![Version](https://img.shields.io/badge/Version-2.0-yellow.svg)

---

## 📋 Project Overview

TrustLink is a sophisticated web application designed to identify phishing threats through advanced pattern recognition and machine learning. The application features a striking cybersecurity-themed interface with a high-tech "dark mode command center" aesthetic.

### Key Features

#### Core Features
✅ **Real-time URL Analysis** - Instant threat detection with sub-second response times  
✅ **Machine Learning Powered** - Scikit-learn models trained for accurate predictions  
✅ **Confidence Scoring** - Transparent probability scores for each prediction  
✅ **Multi-layer Detection** - Pattern recognition, domain analysis, and behavioral detection  
✅ **Intuitive UI** - Clean, modern interface with visual threat indicators

#### New in v2.0 🆕
✅ **User Authentication** - Secure account system with session management  
✅ **Personal Dashboard** - Statistics, history, and quick actions  
✅ **Scan History Tracking** - Complete audit trail of all analyzed URLs  
✅ **API Key Management** - Generate keys for programmatic access  
✅ **Batch Scanning API** - Analyze up to 100 URLs in one request  
✅ **Advanced ML Features** - Domain age, SSL validation, DNS checks, entropy analysis  
✅ **Analytics Dashboard** - 30-day trends with interactive charts  
✅ **Dual Authentication** - Session-based (web) and API key-based (developers)  

---

## 🏗️ Project Structure

```
TrustLink/
├── app.py                      # Flask backend server
├── models/
│   ├── model.pkl              # Pre-trained ML model (Logistic Regression)
│   └── vectorizer.pkl         # TF-IDF vectorizer
├── templates/
│   ├── base.html              # Base HTML template
│   └── index.html             # Main scanner page
├── static/
│   ├── css/
│   │   └── style.css          # Cybersecurity-themed styling
│   └── js/
│       └── main.js            # Frontend logic & AJAX handling
└── README.md                  # This file
```

---

## 🎨 Design Aesthetic

### Color Palette
- **Backgrounds**: Deep blacks (#0a0a0a, #121212) and charcoal grays (#1e1e1e)
- **Primary Accent**: Cautionary Yellow/Gold (#FFD700, #F4C430)
- **Text**: Off-white (#e0e0e0) with yellow accents for emphasis
- **Status Colors**: 
  - ✅ Bright Green (#00ff88) for "Safe" results
  - ⚠️ Alarming Red (#ff3b3b) for "Phishing" results

### Visual Elements
- Clean sans-serif fonts (Inter, Roboto Mono)
- Subtle circuit board patterns and hexagonal mesh backgrounds
- Shield/padlock iconography
- Glowing accent effects on interactive elements

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
pip install flask scikit-learn numpy
```

### Step 2: Verify Project Structure

Ensure all files are in place:
- ✓ `app.py` exists
- ✓ `models/` directory contains `model.pkl` and `vectorizer.pkl`
- ✓ `templates/` contains `base.html` and `index.html`
- ✓ `static/css/style.css` exists
- ✓ `static/js/main.js` exists

### Step 3: Run the Application

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`

### Step 4: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

---

## 🔧 How It Works

### Backend Flow

1. **Model Loading**: Flask loads pre-trained `model.pkl` and `vectorizer.pkl` on startup
2. **URL Submission**: User submits a URL through the web interface
3. **Feature Extraction**: Backend extracts URL features:
   - Domain analysis
   - Path length calculation
   - IP address detection
   - Suspicious TLD identification (.tk, .ml, .ga, .xyz, .ru)
   - Login keyword detection (login, verify, account, secure, update)
4. **Vectorization**: URL is transformed using TF-IDF vectorizer
5. **Prediction**: Model predicts Safe (0) or Phishing (1) with confidence score
6. **Response**: JSON response sent back to frontend

### Frontend Flow

1. **Form Submission**: User enters URL and clicks "Analyze"
2. **AJAX Request**: JavaScript sends POST request to `/predict` endpoint
3. **Loading State**: Displays animated spinner during processing
4. **Result Display**: Updates UI with:
   - Threat assessment (Safe/Phishing)
   - Confidence score with animated progress bar
   - Risk level indicator
   - Detailed feature analysis
5. **Visual Feedback**: Color-coded results with appropriate icons

---

## 📡 API Endpoints

### `GET /`
Returns the main scanner page (HTML)

### `POST /predict`
Analyzes a URL for phishing threats

**Request Body:**
```json
{
  "url": "http://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "url": "http://example.com",
  "prediction": "Safe",
  "confidence": 92.45,
  "details": {
    "domain": "example.com",
    "path_length": 0,
    "has_ip_address": false,
    "suspicious_tld": false,
    "login_keywords_detected": false
  },
  "risk_level": "low"
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "vectorizer_loaded": true
}
```

---

## 🧪 Testing the Application

### Manual Testing

1. **Test Safe URL:**
   ```
   http://google.com/search
   http://github.com/repository
   ```

2. **Test Suspicious URLs:**
   ```
   http://paypal-secure-login.xyz/verify
   http://bank-verify-account.ru/update
   http://192.168.1.1/login
   ```

### API Testing with cURL

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test prediction endpoint
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "http://suspicious-site.tk/login"}'
```

### Python Testing Script

```python
import requests

url = "http://localhost:5000/predict"
data = {"url": "http://paypal-verify.xyz/account"}

response = requests.post(url, json=data)
print(response.json())
```

---

## 🎯 Feature Extraction Details

The application extracts the following features from URLs:

| Feature | Description | Risk Indicator |
|---------|-------------|----------------|
| **Domain** | The main domain name | Used for reputation analysis |
| **Path Length** | Number of characters in URL path | Very long paths can be suspicious |
| **IP Address** | Whether URL contains raw IP | Direct IPs often indicate phishing |
| **Suspicious TLD** | Top-level domains (.tk, .ml, .ga, .xyz, .ru) | These TLDs are commonly abused |
| **Login Keywords** | Keywords like "login", "verify", "account" | Phishing often mimics login pages |

---

## 🔮 Future Enhancements

- [ ] Real-time database of known phishing domains
- [ ] SSL certificate validation
- [ ] WHOIS domain age checking
- [ ] URL redirection analysis
- [ ] Browser extension integration
- [ ] User reporting system
- [ ] Historical threat analytics dashboard
- [ ] Multi-language support
- [ ] API rate limiting and authentication

---

## 🛡️ Security Considerations

**Note:** This is a prototype/demonstration application. For production use:

1. Implement proper input validation and sanitization
2. Add rate limiting to prevent abuse
3. Use HTTPS for all communications
4. Implement user authentication if needed
5. Add comprehensive logging and monitoring
6. Use a production WSGI server (Gunicorn, uWSGI)
7. Implement CORS policies appropriately
8. Regular model retraining with updated threat data

---

## 📚 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Flask | Web server and API routing |
| **ML Framework** | Scikit-learn | Model training and prediction |
| **Vectorization** | TF-IDF | Text feature extraction |
| **Model** | Logistic Regression | Binary classification (Safe/Phishing) |
| **Frontend** | HTML5, CSS3, Vanilla JS | User interface |
| **Icons** | Font Awesome 6 | Visual iconography |
| **Fonts** | Inter, Roboto Mono | Typography |

---

## 👨‍💻 Development Notes

### Dummy Model Information
The included `model.pkl` and `vectorizer.pkl` are trained on a minimal dataset for demonstration purposes. In production:

1. Train on a large, diverse dataset of phishing and legitimate URLs
2. Include features like domain age, SSL status, page content analysis
3. Implement ensemble methods (Random Forest, Gradient Boosting)
4. Regular model updates with new threat intelligence

### Customization
- **Colors**: Edit CSS variables in `static/css/style.css`
- **Model**: Replace `models/model.pkl` with your trained model
- **Features**: Extend `extract_features_from_url()` in `app.py`
- **UI**: Modify templates in `templates/` directory

---

## 📝 License

This project is created for educational and demonstration purposes.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

## 📧 Contact

For questions or feedback about this project, please open an issue on the repository.

---

**Built with ❤️ for cybersecurity education**


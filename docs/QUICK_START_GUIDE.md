# TrustLink - Quick Start Guide 🚀

## What's New?

Three major improvements have been implemented:

1. **🤖 Automatic ML Training** - Machine learning model trains automatically
2. **💬 Working AI Chatbot** - Fixed and enhanced with better error handling
3. **🌙 Dark Mode** - Beautiful dark theme with toggle button

---

## Getting Started (3 Steps)

### Step 1: Configure Environment
```bash
# Copy .env.example to .env if you haven't already
cp .env.example .env

# Edit .env and set (optional):
CHATBOT_ENABLED=true
AUTO_ML_TRAINING=true
```

### Step 2: Start the Server
```bash
python app.py
```

You should see:
```
✓ AI Chatbot enabled
✓ Automatic ML training will start with server
✓ Background ML training scheduler initialized
📅 Next training scheduled for: [timestamp]
Starting Flask server...
```

### Step 3: Open Your Browser
```
http://localhost:5000
```

---

## Testing the New Features

### 🌙 Test Dark Mode
1. Look at the **top-right corner** for the theme toggle button
2. Click it to switch between light and dark modes
3. Refresh the page - your choice is saved!
4. The theme auto-detects your system preference

**Features:**
- Beautiful dark navy background
- Cyan and purple accents
- Smooth transitions
- Eye-friendly colors
- Works on all pages

### 💬 Test AI Chatbot
1. Look at the **bottom-right corner** for the chat icon
2. Click it to open the chatbot
3. Try asking: "How does TrustLink detect phishing?"
4. Wait 10-20 seconds on first request (model loads)

**Features:**
- Free Hugging Face API
- No API key required
- Context-aware responses
- Suggested questions
- Fallback responses if API is down

### 🤖 Test ML Training
ML training happens automatically! You'll see:
- Training scheduled at server startup
- Daily retraining at 2 AM UTC
- Model metrics updated automatically

**To verify:**
```bash
# Check server logs for:
✓ Background ML training scheduler initialized
📅 Next training scheduled for: [date/time]
```

---

## Configuration Options

### Disable Auto ML Training
```bash
# In .env
AUTO_ML_TRAINING=false
```

### Disable Chatbot
```bash
# In .env
CHATBOT_ENABLED=false
```

### Use OpenAI Instead of Hugging Face
```bash
# In .env
CHATBOT_PROVIDER=openai
OPENAI_API_KEY=your-key-here
```

---

## File Structure

### New Files:
```
static/css/dark-mode.css      # Dark mode styles
static/js/dark-mode.js         # Theme toggle logic
IMPROVEMENTS_COMPLETED.md      # Detailed documentation
QUICK_START_GUIDE.md          # This file
```

### Modified Files:
```
app.py                        # Added ML training scheduler
chatbot.py                    # Fixed errors, better handling
templates/base.html           # Added dark mode includes
.env.example                  # Added new config options
```

---

## Troubleshooting

### Dark Mode Not Working?
- Clear browser cache (Ctrl+F5)
- Check browser console for errors
- Verify dark-mode.js is loaded

### Chatbot Not Responding?
- Wait 10-20 seconds (model loading on first request)
- Check CHATBOT_ENABLED=true in .env
- Look at server logs for errors

### ML Training Not Starting?
- Check AUTO_ML_TRAINING=true in .env
- Verify background_scheduler.py exists
- Check server logs for scheduler messages

---

## What Happens Automatically?

### On Server Start:
1. ✅ Dark mode system initializes
2. ✅ Chatbot connects to API
3. ✅ ML training scheduler starts
4. ✅ Next training scheduled

### Every Day at 2 AM UTC:
1. 📥 Fetch new phishing URLs from APIs
2. 🧠 Retrain ML model with new data
3. 📊 Update model metrics
4. 💾 Save improved model

### When User Opens Website:
1. 🎨 Dark mode applies user preference
2. 💬 Chatbot loads and waits for questions
3. 🔍 Scanner ready with latest model

---

## Key Benefits

### For Users:
- 👁️ Comfortable dark mode for night usage
- 💬 Instant help from AI assistant
- 🎯 More accurate phishing detection

### For Developers:
- 🤖 Automated ML training (no manual work)
- 🔄 Model improves automatically
- 🛠️ Better error handling and logging

### For Security:
- 📈 Continuously learning from new threats
- 🌐 External threat intelligence integration
- 🔒 No degradation in model accuracy

---

## Next Steps

### Try These:
1. **Scan a URL** - Test the phishing detector
2. **Toggle Dark Mode** - See the beautiful theme
3. **Ask the Chatbot** - "What is phishing?"
4. **Check History** - View your scan results
5. **Explore Analytics** - See system statistics

### Advanced Configuration:
- Set up email notifications
- Configure external APIs (VirusTotal, Google Safe Browsing)
- Customize ML training schedule
- Add custom dark mode colors

---

## Support

For issues or questions:
1. Check `IMPROVEMENTS_COMPLETED.md` for detailed docs
2. Review server logs for errors
3. Check browser console for JavaScript errors
4. Verify `.env` configuration

---

**Enjoy your enhanced TrustLink! 🛡️**

The system is now:
- 🤖 Learning automatically
- 💬 Answering questions intelligently  
- 🌙 Looking beautiful in any mode

---

*Ready to protect users from phishing threats!*

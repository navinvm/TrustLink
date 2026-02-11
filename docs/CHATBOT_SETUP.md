# 🤖 TrustLink AI Chatbot - Setup Guide

The TrustLink AI Chatbot is an intelligent assistant that helps users understand phishing threats, interpret scan results, and learn about online security.

## ✨ Features

- **AI-Powered Assistance**: Uses OpenAI GPT-4o-mini for intelligent, context-aware responses
- **Context Integration**: Automatically includes user scan history and statistics
- **Security Expertise**: Specialized knowledge in phishing detection and cybersecurity
- **Beautiful UI**: Modern glassmorphic design with floating chat widget
- **Mobile Responsive**: Works seamlessly on all devices
- **Dark Mode Support**: Automatically adapts to user preferences
- **Conversation History**: Maintains context across multiple messages

## 📦 What's Been Implemented

### 1. Backend API (`app.py`)
- ✅ `/api/chat` - Main chat endpoint with conversation history
- ✅ `/api/chat/suggestions` - Get suggested starter questions
- ✅ `/api/chat/quick-response/<type>` - Quick response templates
- ✅ `/api/chat/status` - Check if chatbot is enabled

### 2. AI Logic (`chatbot.py`)
- ✅ TrustLinkChatbot class with OpenAI integration
- ✅ Context-aware responses using user statistics
- ✅ Customized system prompt for security expertise
- ✅ Conversation history management
- ✅ Error handling and fallback messages

### 3. Frontend Widget (`static/js/chatbot.js`)
- ✅ Floating chat button with smooth animations
- ✅ Chat window with header, messages, and input
- ✅ Typing indicators and message formatting
- ✅ Suggested questions for first-time users
- ✅ Auto-scrolling and responsive design

### 4. Styling (`static/css/chatbot.css`)
- ✅ Glassmorphic design with backdrop blur
- ✅ Gradient backgrounds and smooth transitions
- ✅ Dark mode support with media queries
- ✅ Mobile-responsive breakpoints
- ✅ Accessibility features

### 5. Integration
- ✅ Added to `base.html` template (available on all pages)
- ✅ Environment configuration in `.env`
- ✅ OpenAI package in `requirements.txt`

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install openai
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Step 2: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you won't be able to see it again!)

### Step 3: Configure Environment

Edit your `.env` file:

```env
# AI Chatbot Configuration
OPENAI_API_KEY=sk-your-api-key-here
CHATBOT_ENABLED=true
```

### Step 4: Restart Server

```bash
python app.py
```

You should see:
```
✓ AI Chatbot enabled
```

### Step 5: Test It Out!

1. Open any page on your TrustLink site
2. Look for the purple floating button in the bottom-right corner
3. Click it to open the chat widget
4. Try asking: "How does TrustLink detect phishing?"

## 🎯 Usage Examples

### For Users

**Starter Questions:**
- "How does TrustLink detect phishing?"
- "What should I do if I find a suspicious URL?"
- "How can I tell if an email is phishing?"
- "What are common signs of a phishing website?"
- "Is HTTPS always safe?"

**Context-Aware Questions:**
- "Can you explain my last scan result?" (after performing a scan)
- "Why was that URL marked as phishing?"
- "What does the confidence score mean?"

### For Developers

**API Usage:**

```javascript
// Send a message to the chatbot
fetch('/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'How does phishing detection work?',
        history: [] // Optional: previous conversation
    })
})
.then(res => res.json())
.then(data => {
    console.log(data.message); // AI response
    console.log(data.tokens_used); // Token usage
});
```

**Check Status:**

```javascript
fetch('/api/chat/status')
    .then(res => res.json())
    .then(data => {
        console.log(data.enabled); // true/false
    });
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | None | Your OpenAI API key (required) |
| `CHATBOT_ENABLED` | false | Enable/disable the chatbot |

### Chatbot Settings (in `chatbot.py`)

```python
# Model selection
model="gpt-4o-mini"  # Cost-effective option

# Response length
max_tokens=500  # Keep responses concise

# Creativity level
temperature=0.7  # Balanced creativity and consistency

# Conversation history
max_history_length=10  # Last 10 messages for context
```

## 💡 Customization

### Change the Avatar Icon

Edit `static/js/chatbot.js` and `static/css/chatbot.css` to modify the SVG icon.

### Modify System Prompt

Edit `chatbot.py` - `get_system_prompt()` method to change the AI's personality and knowledge.

### Change Colors

Edit `static/css/chatbot.css`:

```css
/* Main gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your brand colors */
background: linear-gradient(135deg, #yourcolor1 0%, #yourcolor2 100%);
```

### Add Custom Quick Responses

Edit `chatbot.py` - `get_quick_responses()` method:

```python
def get_quick_responses(self):
    return {
        'welcome': 'Your custom welcome message',
        'help': 'Your custom help message',
        # Add more custom responses
    }
```

## 🔒 Security & Privacy

- **User Context**: Only includes scan history for logged-in users
- **Rate Limiting**: Uses existing rate limiting infrastructure
- **Message Validation**: Input sanitization and length limits
- **No Data Storage**: Conversations are not permanently stored
- **Session-Based**: History is maintained in browser session only

## 💰 Cost Considerations

The chatbot uses GPT-4o-mini which is cost-effective:

- **Input**: ~$0.15 per 1M tokens
- **Output**: ~$0.60 per 1M tokens

Typical conversation costs:
- Average message: ~100-200 tokens
- Average response: ~200-400 tokens
- Cost per exchange: ~$0.0001-0.0003 (less than a penny)

For 1000 conversations/month: ~$0.20-0.50/month

## 🐛 Troubleshooting

### Chatbot button doesn't appear

1. Check browser console for errors
2. Verify `chatbot.css` and `chatbot.js` are loaded
3. Check if chatbot is enabled: visit `/api/chat/status`

### "Chatbot is currently disabled" error

1. Verify `OPENAI_API_KEY` is set in `.env`
2. Verify `CHATBOT_ENABLED=true` in `.env`
3. Check console for: `✓ AI Chatbot enabled`
4. Restart the server after changing `.env`

### OpenAI API errors

1. Verify your API key is valid
2. Check your OpenAI account has credits
3. Ensure `openai` package is installed: `pip install openai`
4. Check OpenAI service status

### Chatbot responds with errors

1. Check server logs for detailed error messages
2. Verify OpenAI API key permissions
3. Check rate limits on your OpenAI account

## 🧪 Testing

### Test Page

Open `tmp_rovodev_test_chatbot.html` in your browser while the server is running to:
- Check chatbot status
- See setup instructions
- Test the chat widget UI

### Manual Testing

1. **Status Check**: Visit `/api/chat/status`
2. **Suggestions**: Visit `/api/chat/suggestions`
3. **Quick Response**: Visit `/api/chat/quick-response/welcome`

### Python Testing

```python
from chatbot import TrustLinkChatbot

# Initialize
bot = TrustLinkChatbot()

# Check if enabled
print(bot.is_enabled())

# Test response
response = bot.generate_response("How does phishing work?")
print(response['message'])
```

## 📚 Architecture

```
┌─────────────────────────────────────────┐
│         Browser (User Interface)        │
│  ┌───────────────────────────────────┐  │
│  │   Floating Chat Widget (JS/CSS)   │  │
│  └───────────────┬───────────────────┘  │
└──────────────────┼──────────────────────┘
                   │ AJAX Requests
┌──────────────────┼──────────────────────┐
│                  ▼                       │
│         Flask Backend (app.py)          │
│  ┌───────────────────────────────────┐  │
│  │     /api/chat Route Handler       │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│  ┌───────────────▼───────────────────┐  │
│  │   TrustLinkChatbot (chatbot.py)  │  │
│  │  • Context gathering              │  │
│  │  • History management             │  │
│  │  • Prompt engineering             │  │
│  └───────────────┬───────────────────┘  │
└──────────────────┼──────────────────────┘
                   │ API Call
┌──────────────────▼──────────────────────┐
│         OpenAI API (GPT-4o-mini)        │
│         Returns AI Response             │
└─────────────────────────────────────────┘
```

## 🎨 UI Features

- **Smooth Animations**: CSS transitions for all interactions
- **Typing Indicator**: Shows when AI is thinking
- **Auto-resize Input**: Text area expands as you type
- **Message History**: Scrollable conversation view
- **Suggested Questions**: Quick-start for new users
- **Mobile Optimized**: Full-screen on small devices
- **Accessibility**: ARIA labels and keyboard navigation

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Save conversation history to database
- [ ] Export chat transcripts
- [ ] Custom training on TrustLink-specific data
- [ ] Integration with scan results page
- [ ] Proactive suggestions based on user behavior
- [ ] Admin dashboard for chat analytics

## 📄 Files Created

1. **Backend**:
   - `chatbot.py` - AI logic and OpenAI integration
   - `app.py` - API routes (4 new endpoints added)

2. **Frontend**:
   - `static/js/chatbot.js` - Chat widget logic
   - `static/css/chatbot.css` - Widget styling

3. **Configuration**:
   - `.env` - Environment variables
   - `requirements.txt` - OpenAI dependency

4. **Documentation**:
   - `CHATBOT_SETUP.md` - This file
   - `tmp_rovodev_test_chatbot.html` - Test page

## ✅ Summary

The AI chatbot is **fully implemented and ready to use**! Just add your OpenAI API key to get started.

**Status**: ✅ Complete
- Backend API: ✅
- AI Logic: ✅
- Frontend Widget: ✅
- Styling: ✅
- Documentation: ✅

Happy chatting! 🤖✨

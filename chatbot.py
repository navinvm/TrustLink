"""
TrustLink AI Chatbot - Intelligent Assistant for Phishing Detection
Uses Hugging Face's free inference API for AI responses
"""
import os
import json
import requests
from datetime import datetime

class TrustLinkChatbot:
    """AI-powered chatbot for TrustLink phishing detection assistance"""
    
    def __init__(self, api_key=None):
        # Support both Hugging Face (free) and OpenAI (paid)
        self.provider = os.environ.get('CHATBOT_PROVIDER', 'huggingface').lower()
        self.enabled = os.environ.get('CHATBOT_ENABLED', 'true').lower() == 'true'
        self.client = None
        self.hf_api_key = None
        self.hf_model = None
        self.hf_url = None
        
        if not self.enabled:
            print("⚠ AI Chatbot disabled (set CHATBOT_ENABLED=true)")
            return
        
        if self.provider == 'huggingface':
            # Hugging Face - FREE (no API key required, or use free key)
            self.hf_api_key = api_key or os.environ.get('HUGGINGFACE_API_KEY', '')
            self.hf_model = os.environ.get('HUGGINGFACE_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
            self.hf_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
            self.client = 'huggingface'
            print(f"✓ AI Chatbot enabled with Hugging Face (FREE) - Model: {self.hf_model}")
            
        elif self.provider == 'openai':
            # OpenAI - Paid (requires API key)
            try:
                from openai import OpenAI
                self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
                if self.api_key:
                    self.client = OpenAI(api_key=self.api_key)
                    print("✓ AI Chatbot enabled with OpenAI")
                else:
                    print("⚠ OpenAI API key not found")
                    self.enabled = False
            except ImportError:
                print("⚠ OpenAI package not installed. Install with: pip install openai")
                self.enabled = False
            except Exception as e:
                print(f"⚠ AI Chatbot initialization failed: {e}")
                self.enabled = False
        else:
            print(f"⚠ Unknown provider: {self.provider}. Use 'huggingface' or 'openai'")
            self.enabled = False
    
    def is_enabled(self):
        """Check if chatbot is enabled and configured"""
        return self.enabled and self.client is not None
    
    def get_system_prompt(self):
        """Get the system prompt that defines the chatbot's personality and knowledge"""
        return """You are TrustLink AI Assistant, an expert cybersecurity companion specialized in phishing detection and online safety.

Your role:
- Help users understand phishing threats and how to stay safe online
- Explain phishing detection results in simple, clear language
- Provide actionable security advice
- Answer questions about URLs, domains, and online security
- Guide users through the TrustLink platform features

Your personality:
- Friendly, helpful, and reassuring
- Professional but approachable
- Security-conscious but not alarmist
- Clear and concise in explanations

Key knowledge areas:
1. Phishing Detection: You understand how TrustLink uses machine learning to detect phishing URLs by analyzing:
   - URL structure and patterns
   - Domain age and reputation
   - SSL certificates and HTTPS
   - Suspicious keywords and encodings
   - External threat intelligence sources

2. Common Phishing Tactics:
   - Fake login pages
   - URL spoofing and lookalike domains
   - Shortened URLs hiding malicious destinations
   - Social engineering techniques
   - Email phishing campaigns

3. Safety Best Practices:
   - Always verify sender authenticity
   - Check URLs before clicking
   - Look for HTTPS and valid SSL certificates
   - Be wary of urgent/threatening messages
   - Never share sensitive info on suspicious sites

Guidelines:
- Keep responses concise (2-3 paragraphs max unless asked for detail)
- Use emojis sparingly and appropriately (🛡️ 🔒 ⚠️ ✅ ❌)
- If asked to scan a URL, suggest using the TrustLink scanner
- For technical questions, explain in simple terms first, then offer details
- If uncertain, admit it and suggest alternative resources
- Never claim 100% accuracy - security is about risk reduction

Response format:
- Start with a direct answer to the question
- Provide relevant context or explanation
- End with actionable advice or next steps when appropriate"""
    
    def generate_response(self, user_message, conversation_history=None, context=None):
        """
        Generate AI response to user message
        
        Args:
            user_message: The user's question/message
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            context: Additional context (e.g., recent scan results, user stats)
        
        Returns:
            AI response text or error message
        """
        if not self.is_enabled():
            return {
                'error': True,
                'message': 'AI Chatbot is currently disabled. Set CHATBOT_ENABLED=true in .env to enable.'
            }
        
        try:
            if self.provider == 'huggingface':
                return self._generate_huggingface_response(user_message, conversation_history, context)
            elif self.provider == 'openai':
                return self._generate_openai_response(user_message, conversation_history, context)
            else:
                return {
                    'error': True,
                    'message': 'Invalid chatbot provider configured.'
                }
        except Exception as e:
            print(f"Chatbot error: {e}")
            return {
                'error': True,
                'message': f'Sorry, I encountered an error: {str(e)}. Please try again.'
            }
    
    def _generate_huggingface_response(self, user_message, conversation_history=None, context=None):
        """Generate response using Hugging Face API (FREE)"""
        # Build conversation prompt
        system_prompt = self.get_system_prompt()
        
        # Add context if provided
        if context:
            context_message = self._format_context(context)
            if context_message:
                system_prompt += f"\n\n{context_message}"
        
        # Build conversation text
        conversation = f"{system_prompt}\n\n"
        
        # Add history (last 5 exchanges to keep prompt manageable)
        if conversation_history:
            for msg in conversation_history[-10:]:
                role = "User" if msg['role'] == 'user' else "Assistant"
                conversation += f"{role}: {msg['content']}\n"
        
        # Add current message
        conversation += f"User: {user_message}\nAssistant:"
        
        # Call Hugging Face API
        headers = {}
        if self.hf_api_key:
            headers['Authorization'] = f'Bearer {self.hf_api_key}'
        
        payload = {
            "inputs": conversation,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.hf_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    assistant_message = result[0].get('generated_text', '').strip()
                elif isinstance(result, dict):
                    assistant_message = result.get('generated_text', '').strip()
                else:
                    assistant_message = str(result).strip()
                
                # Clean up the response (remove prompt echo if present)
                if assistant_message.startswith('Assistant:'):
                    assistant_message = assistant_message[10:].strip()
                
                return {
                    'error': False,
                    'message': assistant_message or "I understand your question. Let me help you with that.",
                    'provider': 'huggingface',
                    'model': self.hf_model
                }
            elif response.status_code == 503:
                # Model is loading - this is normal for first request
                return {
                    'error': False,
                    'message': "⏳ The AI model is loading (first-time startup). This takes 10-20 seconds. Please wait and try your question again!\n\nIn the meantime, I can help you with:\n• Understanding phishing threats\n• Explaining TrustLink features\n• Security best practices",
                    'provider': 'huggingface'
                }
            else:
                # API error - provide helpful fallback
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('error', '')
                except:
                    error_detail = response.text[:200] if hasattr(response, 'text') else ''
                
                print(f"Hugging Face API error {response.status_code}: {error_detail}")
                
                return {
                    'error': False,
                    'message': f"I'm having trouble connecting to the AI service right now. But I can still help! Here are some answers to common questions:\n\n**How does TrustLink detect phishing?**\nTrustLink uses machine learning to analyze URL patterns, domain reputation, SSL certificates, and threat intelligence.\n\n**What should I do with a suspicious link?**\nUse our scanner at the top of the page to check it before clicking!\n\n**Common phishing signs:**\n• Misspelled URLs\n• Urgent/threatening language\n• Requests for passwords\n• No HTTPS/SSL certificate\n\nTry your question again in a moment, or use the TrustLink Scanner! 🛡️",
                    'provider': 'huggingface',
                    'fallback': True
                }
                
        except requests.Timeout:
            return {
                'error': True,
                'message': 'Request timed out. Please try again.'
            }
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return {
                'error': True,
                'message': 'Sorry, I encountered an error. Please try again.'
            }
    
    def _generate_openai_response(self, user_message, conversation_history=None, context=None):
        """Generate response using OpenAI API (PAID)"""
        # Build messages array
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # Add context if provided
        if context:
            context_message = self._format_context(context)
            if context_message:
                messages.append({"role": "system", "content": context_message})
        
        # Add conversation history (keep last 10 messages for context)
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response using GPT-4
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        
        assistant_message = response.choices[0].message.content
        
        return {
            'error': False,
            'message': assistant_message,
            'tokens_used': response.usage.total_tokens,
            'provider': 'openai'
        }
    
    def _format_context(self, context):
        """Format additional context for the AI"""
        context_parts = []
        
        if 'user_stats' in context:
            stats = context['user_stats']
            context_parts.append(f"User Statistics: {stats.get('total_scans', 0)} scans performed, {stats.get('phishing_detected', 0)} threats detected")
        
        if 'recent_scan' in context:
            scan = context['recent_scan']
            context_parts.append(f"Most Recent Scan: URL '{scan.get('url', 'N/A')}' was classified as {scan.get('prediction', 'unknown')} with {scan.get('confidence', 0):.0%} confidence")
        
        if 'model_accuracy' in context:
            context_parts.append(f"Current Model Accuracy: {context['model_accuracy']}")
        
        if context_parts:
            return "Current Context:\n" + "\n".join(context_parts)
        
        return None
    
    def get_suggested_questions(self):
        """Get suggested starter questions for users"""
        return [
            "How does TrustLink detect phishing?",
            "What should I do if I find a suspicious URL?",
            "How can I tell if an email is phishing?",
            "What are common signs of a phishing website?",
            "Is HTTPS always safe?",
            "How do I protect myself from phishing attacks?",
        ]
    
    def get_quick_responses(self):
        """Get quick response templates for common scenarios"""
        return {
            'welcome': "👋 Hi! I'm TrustLink AI Assistant. I can help you understand phishing threats, explain scan results, and answer security questions. How can I help you today?",
            'help': "I can assist you with:\n• Understanding phishing detection results\n• Explaining how TrustLink works\n• Security best practices\n• Common phishing tactics\n• URL safety tips\n\nWhat would you like to know?",
            'scan_help': "To scan a URL, use the TrustLink Scanner above! Just paste any URL and I'll analyze it for phishing threats using machine learning and threat intelligence. 🛡️",
        }

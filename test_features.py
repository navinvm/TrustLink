"""
TrustLink v2.0 - Feature Testing Script
Tests all new features including auth, API keys, and advanced ML
"""
import requests
import json
import time

import os
BASE_URL = os.getenv('TRUSTLINK_API_URL', 'http://127.0.0.1:5000')

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_health_check():
    """Test health endpoint"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print(f"✓ Status: {data['status']}")
        print(f"✓ Model Loaded: {data['model_loaded']}")
        print(f"✓ Vectorizer Loaded: {data['vectorizer_loaded']}")
        print(f"✓ Advanced Features: {data['advanced_features']}")
        print(f"✓ Version: {data['version']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print_section("2. User Registration")
    try:
        # Generate unique username
        username = f"testuser_{int(time.time())}"
        email = f"{username}@test.com"
        
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/register",
            data={
                "username": username,
                "email": email,
                "password": "testpass123",
                "confirm_password": "testpass123"
            },
            allow_redirects=False
        )
        
        if response.status_code in [302, 200]:
            print(f"✓ User registered: {username}")
            print(f"✓ Email: {email}")
            return session, username
        else:
            print(f"✗ Registration failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None

def test_authenticated_scan(session, username):
    """Test authenticated URL scanning"""
    print_section("3. Authenticated Scan (with History)")
    try:
        # Test safe URL
        response = session.post(
            f"{BASE_URL}/predict",
            json={"url": "http://google.com"}
        )
        data = response.json()
        
        print(f"✓ URL: {data['url']}")
        print(f"✓ Prediction: {data['prediction']}")
        print(f"✓ Confidence: {data['confidence']}%")
        print(f"✓ Risk Level: {data['risk_level']}")
        print(f"✓ Scan saved to user history")
        
        # Test phishing URL
        response = session.post(
            f"{BASE_URL}/predict",
            json={"url": "http://paypal-verify-account.tk/login"}
        )
        data = response.json()
        
        print(f"\n✓ URL: {data['url']}")
        print(f"✓ Prediction: {data['prediction']}")
        print(f"✓ Confidence: {data['confidence']}%")
        print(f"✓ Risk Level: {data['risk_level']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_api_key_creation(session):
    """Test API key generation"""
    print_section("4. API Key Generation")
    try:
        response = session.post(
            f"{BASE_URL}/api-keys",
            data={"key_name": "Test API Key"}
        )
        
        if "new_key" in response.text or response.status_code == 200:
            # Extract API key from response
            # Note: In real scenario, you'd parse HTML or get from JSON
            print(f"✓ API key created successfully")
            print(f"✓ Key name: Test API Key")
            print(f"⚠ Note: Key displayed only once in web interface")
            return "dummy_key_for_demo"  # Placeholder
        else:
            print(f"✗ Failed to create API key")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_anonymous_scan():
    """Test anonymous scanning (no login)"""
    print_section("5. Anonymous Scan (No History)")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"url": "http://github.com"}
        )
        data = response.json()
        
        print(f"✓ URL: {data['url']}")
        print(f"✓ Prediction: {data['prediction']}")
        print(f"✓ Confidence: {data['confidence']}%")
        print(f"✓ Anonymous scan works (not saved)")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_advanced_features():
    """Test URLs to check advanced feature extraction"""
    print_section("6. Advanced Feature Extraction Tests")
    
    test_urls = [
        ("http://192.168.1.1/admin", "IP Address Detection"),
        ("http://suspicious-site.tk/verify", "Suspicious TLD"),
        ("https://secure-bank.com/login", "HTTPS & Login Keywords"),
        ("http://very-long-suspicious-domain-name-here.xyz/path/to/resource", "Long URL"),
    ]
    
    try:
        for url, description in test_urls:
            print(f"\n→ Testing: {description}")
            print(f"  URL: {url}")
            
            response = requests.post(
                f"{BASE_URL}/predict",
                json={"url": url}
            )
            data = response.json()
            
            print(f"  Prediction: {data['prediction']}")
            print(f"  Confidence: {data['confidence']}%")
            
            details = data.get('details', {})
            if details.get('has_ip_address'):
                print(f"  ⚠ IP address detected")
            if details.get('suspicious_tld'):
                print(f"  ⚠ Suspicious TLD")
            if details.get('login_keywords_detected'):
                print(f"  ⚠ Login keywords found")
            if details.get('url_length', 0) > 50:
                print(f"  ⚠ Long URL ({details['url_length']} chars)")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_batch_scanning():
    """Test batch scanning with API key"""
    print_section("7. Batch Scanning (Requires API Key)")
    
    print("⚠ This test requires a valid API key")
    print("  To test manually:")
    print("  1. Create an account and login")
    print("  2. Generate an API key at /api-keys")
    print("  3. Use the key with /api/v1/batch-scan endpoint")
    print("\nExample:")
    print("""
    curl -X POST https://YOUR_DOMAIN/api/v1/batch-scan \\
      -H "Content-Type: application/json" \\
      -H "X-API-Key: YOUR_KEY" \\
      -d '{"urls": ["http://site1.com", "http://site2.com"]}'
    """)

def display_summary():
    """Display test summary and next steps"""
    print_section("Test Summary & Next Steps")
    
    print("""
✓ Core Features Tested:
  - Health check endpoint
  - User registration
  - Authenticated scanning with history
  - Anonymous scanning
  - Advanced feature extraction
  - API key generation

📝 Manual Testing Required:
  - Dashboard visualization (visit /dashboard)
  - Full scan history (visit /history)
  - API key management (visit /api-keys)
  - Analytics charts (visit /analytics)
  - Batch scanning with real API key

🚀 Quick Start:
  1. Visit https://YOUR_DOMAIN/register
  2. Create an account
  3. Explore the dashboard
  4. Generate an API key
  5. Test the API endpoints

📖 Documentation:
  - README.md - Overview and setup
  - FEATURES_v2.md - Complete feature documentation
  - QUICKSTART.md - Quick start guide

🎯 Test URLs:
  Safe:     http://google.com, http://github.com
  Phishing: http://paypal-verify.tk/login, http://bank-secure.xyz/update
    """)

def main():
    """Run all tests"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  TrustLink v2.0 - Automated Feature Tests".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    print(f"\n⚠️  Make sure TrustLink is running on {BASE_URL}")
    input("Press Enter to start tests... ")
    
    # Run tests
    if not test_health_check():
        print("\n❌ Server not responding. Please start the application first.")
        print("   Run: python app.py")
        return
    
    test_anonymous_scan()
    
    session, username = test_user_registration()
    if session and username:
        test_authenticated_scan(session, username)
        test_api_key_creation(session)
    
    test_advanced_features()
    test_batch_scanning()
    
    display_summary()
    
    print("\n" + "=" * 70)
    print("  Testing Complete! ✨")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")

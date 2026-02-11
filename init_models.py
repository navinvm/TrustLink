"""
Initialize ML models for serverless deployment
This script trains a basic model if models don't exist
"""
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import numpy as np

def create_basic_model():
    """Create a basic model with sample training data"""
    print("Creating basic phishing detection model...")
    
    # Basic training data (phishing indicators)
    training_urls = [
        # Phishing examples
        "http://paypal-verify.com/login",
        "https://secure-banking-login.tk/",
        "http://amazon-account-verify.ml/",
        "https://facebook-security-check.ga/",
        "http://netflix-billing-update.cf/",
        "https://apple-id-verify.gq/",
        "http://microsoft-account-recovery.tk/",
        "https://instagram-verify-account.ml/",
        "http://twitter-security-alert.ga/",
        "https://linkedin-update-profile.cf/",
        # Legitimate examples
        "https://www.paypal.com/signin",
        "https://www.amazon.com/account",
        "https://www.facebook.com/login",
        "https://www.netflix.com/browse",
        "https://appleid.apple.com/",
        "https://account.microsoft.com/",
        "https://www.instagram.com/accounts/login/",
        "https://twitter.com/login",
        "https://www.linkedin.com/login",
        "https://www.google.com/gmail",
    ]
    
    # Labels: 1 = phishing, 0 = legitimate
    labels = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # First 10 are phishing
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Last 10 are legitimate
    
    # Create vectorizer
    vectorizer = TfidfVectorizer(min_df=1, max_features=1000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(training_urls)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, labels)
    
    return model, vectorizer

def init_models():
    """Initialize models if they don't exist"""
    os.makedirs('models', exist_ok=True)
    
    model_path = 'models/model.pkl'
    vectorizer_path = 'models/vectorizer.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        print("Models not found. Creating basic models...")
        model, vectorizer = create_basic_model()
        
        # Save models
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Model saved to {model_path}")
        
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
        print(f"✓ Vectorizer saved to {vectorizer_path}")
        
        return True
    else:
        print("✓ Models already exist")
        return False

if __name__ == "__main__":
    init_models()

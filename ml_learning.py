"""
TrustLink: Machine Learning Enhancement Module
Implements external API validation and model retraining
"""
import requests
import hashlib
import pickle
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score


class ExternalValidator:
    """
    Validates URLs against external threat intelligence APIs
    Supports: Google Safe Browsing, PhishTank, VirusTotal
    """
    
    def __init__(self, config=None):
        """
        Initialize with API keys
        config = {
            'google_api_key': 'YOUR_KEY',
            'virustotal_api_key': 'YOUR_KEY',
            'phishtank_api_key': 'YOUR_KEY'  # Optional
        }
        """
        self.config = config or {}
        self.google_api_key = self.config.get('google_api_key')
        self.virustotal_api_key = self.config.get('virustotal_api_key')
        self.phishtank_api_key = self.config.get('phishtank_api_key')
    
    def check_google_safe_browsing(self, url):
        """
        Check URL against Google Safe Browsing API
        Returns: {'is_threat': bool, 'threat_type': str or None, 'source': 'google'}
        """
        if not self.google_api_key:
            return {'is_threat': None, 'threat_type': None, 'source': 'google', 'error': 'No API key'}
        
        api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.google_api_key}'
        
        payload = {
            "client": {
                "clientId": "trustlink",
                "clientVersion": "2.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'matches' in data and len(data['matches']) > 0:
                    threat_type = data['matches'][0].get('threatType', 'UNKNOWN')
                    return {
                        'is_threat': True,
                        'threat_type': threat_type,
                        'source': 'google',
                        'confidence': 0.95  # High confidence for Google
                    }
                else:
                    return {
                        'is_threat': False,
                        'threat_type': None,
                        'source': 'google',
                        'confidence': 0.85
                    }
            else:
                return {'is_threat': None, 'error': f'API error: {response.status_code}', 'source': 'google'}
        
        except Exception as e:
            return {'is_threat': None, 'error': str(e), 'source': 'google'}
    
    def check_virustotal(self, url):
        """
        Check URL against VirusTotal API
        Returns: {'is_threat': bool, 'positives': int, 'total': int, 'source': 'virustotal'}
        """
        if not self.virustotal_api_key:
            return {'is_threat': None, 'source': 'virustotal', 'error': 'No API key'}
        
        # URL submission and scan
        headers = {'x-apikey': self.virustotal_api_key}
        api_url = 'https://www.virustotal.com/api/v3/urls'
        
        try:
            # First, submit URL for scanning
            url_id = hashlib.sha256(url.encode()).hexdigest()
            
            # Get URL report
            report_url = f'https://www.virustotal.com/api/v3/urls/{url_id}'
            response = requests.get(report_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                total = sum(stats.values())
                
                is_threat = (malicious + suspicious) > 0
                confidence = min((malicious + suspicious * 0.5) / max(total, 1), 1.0)
                
                return {
                    'is_threat': is_threat,
                    'positives': malicious + suspicious,
                    'total': total,
                    'source': 'virustotal',
                    'confidence': confidence
                }
            elif response.status_code == 404:
                # URL not in database - submit it
                submit_response = requests.post(api_url, headers=headers, data={'url': url}, timeout=5)
                return {
                    'is_threat': None,
                    'source': 'virustotal',
                    'message': 'URL submitted for scanning',
                    'scan_id': submit_response.json().get('data', {}).get('id')
                }
            else:
                return {'is_threat': None, 'error': f'API error: {response.status_code}', 'source': 'virustotal'}
        
        except Exception as e:
            return {'is_threat': None, 'error': str(e), 'source': 'virustotal'}
    
    def check_phishtank(self, url):
        """
        Check URL against PhishTank database (free, no API key needed)
        Returns: {'is_threat': bool, 'source': 'phishtank'}
        """
        api_url = 'https://checkurl.phishtank.com/checkurl/'
        
        try:
            # PhishTank requires POST with specific format
            data = {
                'url': url,
                'format': 'json'
            }
            
            headers = {
                'User-Agent': 'TrustLink/2.0'
            }
            
            response = requests.post(api_url, data=data, headers=headers, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'results' in result:
                    is_phishing = result['results'].get('in_database', False)
                    verified = result['results'].get('verified', False)
                    
                    return {
                        'is_threat': is_phishing,
                        'verified': verified,
                        'source': 'phishtank',
                        'confidence': 0.9 if verified else 0.7
                    }
            
            return {'is_threat': False, 'source': 'phishtank', 'confidence': 0.6}
        
        except Exception as e:
            return {'is_threat': None, 'error': str(e), 'source': 'phishtank'}
    
    def validate_url(self, url, use_all=True):
        """
        Validate URL against multiple sources and aggregate results
        Uses parallel execution for faster validation
        Returns: {
            'is_threat': bool,
            'confidence': float,
            'sources': list of results,
            'consensus': str
        }
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        api_checks = []
        
        # Prepare API checks
        if self.google_api_key:
            api_checks.append(('Google Safe Browsing', self.check_google_safe_browsing))
        
        if self.virustotal_api_key:
            api_checks.append(('VirusTotal', self.check_virustotal))
        
        # PhishTank is free, always check
        api_checks.append(('PhishTank', self.check_phishtank))
        
        # Execute all checks in parallel
        with ThreadPoolExecutor(max_workers=len(api_checks)) as executor:
            # Submit all tasks
            future_to_api = {
                executor.submit(check_func, url): api_name 
                for api_name, check_func in api_checks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_api):
                api_name = future_to_api[future]
                try:
                    result = future.result(timeout=10)
                    results.append(result)
                except Exception as e:
                    print(f"  ⚠️  {api_name} error: {e}")
                    results.append({
                        'is_threat': None,
                        'error': str(e),
                        'source': api_name.lower().replace(' ', '_')
                    })
        
        # Get list of sources checked
        sources_checked = [r.get('source', 'unknown') for r in results]
        
        # Aggregate results
        valid_results = [r for r in results if r.get('is_threat') is not None]
        
        if not valid_results:
            return {
                'is_threat': None,
                'confidence': 0.0,
                'sources': results,
                'sources_checked': sources_checked,
                'consensus': 'unknown',
                'error': 'No valid results from any source'
            }
        
        # Calculate consensus
        threat_votes = sum(1 for r in valid_results if r['is_threat'])
        safe_votes = len(valid_results) - threat_votes
        
        # Weighted confidence based on individual source confidences
        weighted_confidence = sum(
            r.get('confidence', 0.5) * (1 if r['is_threat'] else -1)
            for r in valid_results
        ) / len(valid_results)
        
        # Normalize to 0-1 range
        confidence = (weighted_confidence + 1) / 2
        
        is_threat = threat_votes > safe_votes
        
        if threat_votes == safe_votes:
            consensus = 'split'
        elif threat_votes > safe_votes:
            consensus = 'threat'
        else:
            consensus = 'safe'
        
        return {
            'is_threat': is_threat,
            'confidence': confidence,
            'sources': results,
            'sources_checked': sources_checked,
            'consensus': consensus,
            'threat_votes': threat_votes,
            'safe_votes': safe_votes,
            'total_sources': len(valid_results)
        }


class ModelTrainer:
    """
    Handles model retraining with new verified data
    """
    
    def __init__(self, model_path='models/model.pkl', vectorizer_path='models/vectorizer.pkl'):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.load_model()
    
    def load_model(self):
        """Load existing model and vectorizer"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print("✓ Loaded existing model for retraining")
            return True
        except Exception as e:
            print(f"⚠ Could not load existing model: {e}")
            self.model = None
            self.vectorizer = None
            return False
    
    def train_new_model(self, urls, labels):
        """
        Train a new model from scratch
        urls: list of URL strings
        labels: list of binary labels (1 = phishing, 0 = safe)
        """
        if len(urls) < 10:
            raise ValueError("Need at least 10 samples to train a model")
        
        # Create new vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            analyzer='char'
        )
        
        # Vectorize URLs
        X = self.vectorizer.fit_transform(urls)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'training_samples': len(urls),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✓ Model trained - Accuracy: {accuracy:.2%}, Precision: {precision:.2%}, Recall: {recall:.2%}")
        
        return metrics
    
    def retrain_model(self, new_urls, new_labels, incremental=False):
        """
        Retrain model with new data
        incremental: If True, tries to update existing model (not implemented for RandomForest)
        """
        if not self.model or not self.vectorizer:
            print("⚠ No existing model found, training from scratch")
            return self.train_new_model(new_urls, new_labels)
        
        # For RandomForest, we need to retrain from scratch with combined data
        # In production, you might want to store training data and combine it here
        
        print(f"📚 Retraining with {len(new_urls)} new samples")
        
        # Update vectorizer vocabulary if needed
        X_new = self.vectorizer.transform(new_urls)
        y_new = np.array(new_labels)
        
        # For demonstration, just train on new data
        # In production, combine with historical data
        self.model.fit(X_new, y_new)
        
        # Evaluate on new data
        y_pred = self.model.predict(X_new)
        accuracy = accuracy_score(y_new, y_pred)
        
        print(f"✓ Model retrained - Accuracy on new data: {accuracy:.2%}")
        
        return {
            'accuracy': accuracy,
            'new_samples': len(new_urls),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_model(self):
        """Save model and vectorizer to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            print(f"✓ Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"✗ Error saving model: {e}")
            return False


class APIDataCollector:
    """
    Collects verified phishing/safe URLs from external APIs for model training
    """
    
    def __init__(self, validator):
        self.validator = validator
        self.collected_data = []
    
    def collect_from_phishtank(self, limit=1000):
        """
        Collect verified phishing URLs from PhishTank with caching
        Returns: list of (url, label) tuples where label=1 for phishing
        """
        print(f"📥 Collecting verified phishing URLs from PhishTank...")
        print(f"   Requested limit: {limit}")
        
        import os
        import json
        from datetime import datetime, timedelta
        
        cache_file = 'phishtank_cache.json'
        cache_max_age = timedelta(hours=24)  # Cache for 24 hours
        
        # Try to use cached data first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                    cache_time = datetime.fromisoformat(cache['timestamp'])
                    
                    if datetime.now() - cache_time < cache_max_age:
                        print(f"   ✓ Using cached data from {cache_time.strftime('%Y-%m-%d %H:%M')}")
                        cached_urls = cache['urls'][:limit]
                        print(f"✓ Collected {len(cached_urls)} verified phishing URLs (from cache)")
                        return cached_urls
                    else:
                        print(f"   ⚠️ Cache expired (older than 24 hours)")
            except Exception as e:
                print(f"   ⚠️ Cache read error: {e}")
        
        # Download fresh data
        try:
            # PhishTank provides a verified phishing database
            api_url = 'http://data.phishtank.com/data/online-valid.json'
            
            import requests
            print(f"   Downloading from PhishTank API...")
            response = requests.get(api_url, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total URLs in PhishTank database: {len(data)}")
                
                phishing_urls = []
                verified_count = 0
                
                # Process all entries
                for entry in data:
                    # Check if verified
                    if entry.get('verified') == 'yes' or entry.get('verified') == True:
                        verified_count += 1
                        url = entry.get('url')
                        if url:
                            phishing_urls.append((url, 1))  # 1 = phishing
                
                print(f"   Verified entries found: {verified_count}")
                
                # Cache the data
                try:
                    cache_data = {
                        'timestamp': datetime.now().isoformat(),
                        'urls': phishing_urls,
                        'total_count': len(phishing_urls)
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f)
                    print(f"   ✓ Cached {len(phishing_urls)} URLs for future use")
                except Exception as e:
                    print(f"   ⚠️ Cache write error: {e}")
                
                result = phishing_urls[:limit]
                print(f"✓ Collected {len(result)} verified phishing URLs")
                return result
                
            elif response.status_code == 429:
                print(f"   ⚠️ PhishTank rate limit exceeded!")
                print(f"   💡 The API limits requests. Please wait a few hours and try again.")
                print(f"   💡 Or use cached data if available.")
                return []
            else:
                print(f"✗ PhishTank API error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"✗ Error collecting from PhishTank: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def collect_safe_urls(self, safe_domains_list):
        """
        Generate safe URL samples from known legitimate domains
        safe_domains_list: list of known safe domains
        Returns: list of (url, label) tuples where label=0 for safe
        """
        print(f"📥 Generating safe URL samples...")
        
        safe_urls = []
        for domain in safe_domains_list:
            # Add domain with https
            safe_urls.append((f"https://{domain}", 0))  # 0 = safe
            # Add common pages
            safe_urls.append((f"https://{domain}/about", 0))
            safe_urls.append((f"https://{domain}/contact", 0))
        
        print(f"✓ Generated {len(safe_urls)} safe URL samples")
        return safe_urls
    
    def validate_and_collect(self, urls, min_confidence=0.7, parallel=True, max_workers=5):
        """
        Validate URLs using external APIs and collect high-confidence results
        Now with parallel processing for faster validation!
        
        urls: list of URL strings to validate
        min_confidence: minimum confidence threshold (0-1) to include
        parallel: if True, validate multiple URLs simultaneously
        max_workers: number of parallel workers (default 5 to respect rate limits)
        Returns: list of (url, label) tuples
        """
        print(f"🔍 Validating {len(urls)} URLs with external APIs...")
        print(f"   Mode: {'Parallel ⚡' if parallel else 'Sequential'}")
        
        validated_data = []
        
        if parallel:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            
            # Process URLs in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all validation tasks
                future_to_url = {
                    executor.submit(self.validator.validate_url, url): url 
                    for url in urls
                }
                
                # Collect results as they complete
                completed = 0
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    completed += 1
                    
                    if completed % 10 == 0:
                        print(f"  Progress: {completed}/{len(urls)} URLs validated...")
                    
                    try:
                        result = future.result(timeout=15)
                        
                        # Only include high-confidence results
                        if result and result.get('confidence', 0) >= min_confidence:
                            is_threat = result.get('is_threat', False)
                            label = 1 if is_threat else 0
                            validated_data.append((url, label))
                    
                    except Exception as e:
                        print(f"  ✗ Error validating {url}: {e}")
                        continue
                    
                    # Small delay to respect rate limits (especially VirusTotal)
                    time.sleep(0.2)
        else:
            # Sequential processing (original method)
            import time
            
            for i, url in enumerate(urls):
                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i + 1}/{len(urls)} URLs validated...")
                
                try:
                    result = self.validator.validate_url(url)
                    
                    # Only include high-confidence results
                    if result and result.get('confidence', 0) >= min_confidence:
                        is_threat = result.get('is_threat', False)
                        label = 1 if is_threat else 0
                        validated_data.append((url, label))
                    
                    # Rate limiting - small delay between requests
                    time.sleep(0.5)
                
                except Exception as e:
                    print(f"  ✗ Error validating {url}: {e}")
                    continue
        
        print(f"✓ Collected {len(validated_data)} validated URLs")
        return validated_data
    
    def get_training_dataset(self, phishing_limit=500, safe_domains_limit=100, triple_verify=True):
        """
        Build a complete training dataset from multiple sources
        With triple verification using all 3 APIs for higher quality
        
        Args:
            phishing_limit: max phishing URLs to collect
            safe_domains_limit: number of safe domains to use
            triple_verify: if True, verify URLs with all 3 APIs for highest quality
        
        Returns: (urls, labels) tuple
        """
        all_data = []
        
        # Collect phishing URLs from PhishTank
        phishing_data = self.collect_from_phishtank(limit=phishing_limit)
        
        if triple_verify and phishing_data:
            print(f"\n🔍 TRIPLE VERIFICATION MODE ENABLED")
            print(f"   Verifying PhishTank URLs with Google + VirusTotal...")
            print(f"   This ensures highest quality training data!")
            print()
            
            # Verify phishing URLs with all 3 APIs
            verified_phishing = self._triple_verify_urls(
                [url for url, label in phishing_data],
                expected_label=1  # Expecting phishing
            )
            
            all_data.extend(verified_phishing)
            print(f"   ✓ {len(verified_phishing)} phishing URLs triple-verified")
        else:
            all_data.extend(phishing_data)
        
        # Generate safe URLs from known domains
        safe_domains = [
            'google.com', 'youtube.com', 'facebook.com', 'amazon.com',
            'wikipedia.org', 'twitter.com', 'instagram.com', 'linkedin.com',
            'reddit.com', 'github.com', 'stackoverflow.com', 'microsoft.com',
            'apple.com', 'netflix.com', 'paypal.com', 'ebay.com',
            'cnn.com', 'bbc.com', 'nytimes.com', 'medium.com',
            'github.io', 'medium.com', 'cloudflare.com', 'mozilla.org',
            'w3.org', 'gnu.org', 'apache.org', 'python.org'
        ]
        
        safe_data = self.collect_safe_urls(safe_domains[:safe_domains_limit])
        
        if triple_verify and safe_data:
            print(f"\n🔍 Verifying safe URLs with all APIs...")
            
            # Verify safe URLs with all 3 APIs
            verified_safe = self._triple_verify_urls(
                [url for url, label in safe_data],
                expected_label=0  # Expecting safe
            )
            
            all_data.extend(verified_safe)
            print(f"   ✓ {len(verified_safe)} safe URLs triple-verified")
        else:
            all_data.extend(safe_data)
        
        # Shuffle the data
        import random
        random.shuffle(all_data)
        
        # Separate URLs and labels
        urls = [item[0] for item in all_data]
        labels = [item[1] for item in all_data]
        
        print(f"\n📊 Training Dataset Summary:")
        print(f"  Total samples: {len(urls)}")
        print(f"  Phishing: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
        print(f"  Safe: {len(labels) - sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
        if triple_verify:
            print(f"  Quality: TRIPLE-VERIFIED (highest quality)")
        
        return urls, labels
    
    def _triple_verify_urls(self, urls, expected_label, consensus_threshold=2):
        """
        Verify URLs using all 3 APIs and only keep URLs where APIs agree
        
        Args:
            urls: list of URL strings to verify
            expected_label: 0 for safe, 1 for phishing
            consensus_threshold: minimum number of APIs that must agree (default 2 out of 3)
        
        Returns: list of (url, label) tuples
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        
        verified_data = []
        total = len(urls)
        
        # Use smaller batch to respect rate limits
        batch_size = 50
        
        for batch_start in range(0, total, batch_size):
            batch_urls = urls[batch_start:batch_start + batch_size]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            print(f"   Batch {batch_num}/{total_batches}: Verifying {len(batch_urls)} URLs...")
            
            # Verify batch in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {
                    executor.submit(self.validator.validate_url, url): url 
                    for url in batch_urls
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    
                    try:
                        result = future.result(timeout=15)
                        
                        # Check if we have results from all sources
                        sources_checked = result.get('sources_checked', [])
                        
                        # Count how many APIs agree with expected label
                        valid_sources = [s for s in result.get('sources', []) if s.get('is_threat') is not None]
                        
                        if expected_label == 1:  # Expecting phishing
                            agree_count = sum(1 for s in valid_sources if s.get('is_threat') == True)
                        else:  # Expecting safe
                            agree_count = sum(1 for s in valid_sources if s.get('is_threat') == False)
                        
                        # Only include if consensus threshold is met
                        if agree_count >= consensus_threshold:
                            verified_data.append((url, expected_label))
                    
                    except Exception as e:
                        # Skip URLs that fail verification
                        continue
                    
                    # Small delay to respect rate limits
                    time.sleep(0.15)
            
            # Longer pause between batches to avoid rate limits
            if batch_start + batch_size < total:
                print(f"   Pausing 5 seconds to respect API rate limits...")
                time.sleep(5)
        
        return verified_data


def train_model_from_apis(api_config=None, phishing_limit=2000, safe_limit=200):
    """
    Train/retrain the model using data from external APIs
    api_config: dict with API keys
    phishing_limit: max phishing URLs to collect
    safe_limit: max safe domains to use
    """
    print("=" * 70)
    print("🚀 TRAINING MODEL FROM EXTERNAL API DATA")
    print("=" * 70)
    
    # Initialize validator and collector
    validator = ExternalValidator(api_config or {})
    collector = APIDataCollector(validator)
    
    # Collect training data
    urls, labels = collector.get_training_dataset(
        phishing_limit=phishing_limit,
        safe_domains_limit=safe_limit
    )
    
    if len(urls) < 10:
        print("✗ Not enough data collected. Need at least 10 samples.")
        return None
    
    # Train the model
    print(f"\n🧠 Training model with {len(urls)} samples...")
    trainer = ModelTrainer()
    metrics = trainer.train_new_model(urls, labels)
    
    # Save the model
    print("\n💾 Saving trained model...")
    trainer.save_model()
    
    # Save metrics
    print("💾 Saving model metrics...")
    import json
    from datetime import datetime
    
    metrics_data = {
        'accuracy': metrics['accuracy'],
        'precision': metrics['precision'],
        'recall': metrics['recall'],
        'training_samples': len(urls),
        'last_updated': datetime.now().isoformat(),
        'model_version': '2.0',
        'data_sources': ['PhishTank', 'Legitimate Domains']
    }
    
    with open('model_metrics.json', 'w') as f:
        json.dump(metrics_data, f, indent=4)
    
    print("\n" + "=" * 70)
    print("✅ MODEL TRAINING COMPLETE!")
    print("=" * 70)
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(f"Training Samples: {len(urls):,}")
    print("=" * 70)
    
    return metrics


if __name__ == '__main__':
    print("=" * 60)
    print("🧠 TrustLink ML Learning Module")
    print("=" * 60)
    
    # Demo without real API keys
    print("\n📝 External Validator Demo (requires API keys)")
    validator = ExternalValidator()
    
    print("\n⚠️  To use external validation, provide API keys:")
    print("   - Google Safe Browsing: https://developers.google.com/safe-browsing")
    print("   - VirusTotal: https://www.virustotal.com/gui/join-us")
    print("   - PhishTank: Free (no key needed)")
    
    print("\n💡 Example usage:")
    print("""
    # Validate a single URL
    validator = ExternalValidator({
        'google_api_key': 'YOUR_GOOGLE_KEY',
        'virustotal_api_key': 'YOUR_VT_KEY'
    })
    
    result = validator.validate_url('http://suspicious-site.com')
    print(result)
    
    # Train model from API data
    from ml_learning import train_model_from_apis
    
    metrics = train_model_from_apis(
        api_config={
            'google_api_key': 'YOUR_KEY',
            'virustotal_api_key': 'YOUR_KEY'
        },
        phishing_limit=1000,
        safe_limit=200
    )
    """)

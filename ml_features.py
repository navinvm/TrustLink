"""
Advanced ML Feature Extraction for TrustLink
Comprehensive URL analysis for phishing detection
"""
import re
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import dns.resolver
import whois


class AdvancedFeatureExtractor:
    """Extract sophisticated features from URLs for ML model"""
    
    def __init__(self):
        self.suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.ru', '.cn']
        self.shortener_domains = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly', 'is.gd']
        self.phishing_keywords = [
            'login', 'verify', 'account', 'secure', 'update', 'confirm', 
            'banking', 'suspended', 'locked', 'unusual', 'click', 'here'
        ]
        
        # Whitelist of known legitimate domains
        self.legitimate_domains = {
            # Search engines & browsers
            'google.com', 'www.google.com', 'bing.com', 'www.bing.com',
            'yahoo.com', 'www.yahoo.com', 'duckduckgo.com', 'www.duckduckgo.com',
            'baidu.com', 'www.baidu.com', 'yandex.com', 'www.yandex.com',
            'brave.com', 'www.brave.com', 'opera.com', 'www.opera.com',
            
            # Social media & messaging
            'facebook.com', 'www.facebook.com', 'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
            'instagram.com', 'www.instagram.com', 'linkedin.com', 'www.linkedin.com',
            'reddit.com', 'www.reddit.com', 'tiktok.com', 'www.tiktok.com',
            'whatsapp.com', 'www.whatsapp.com', 'telegram.org', 'www.telegram.org',
            'discord.com', 'www.discord.com', 'slack.com', 'www.slack.com',
            'snapchat.com', 'www.snapchat.com', 'pinterest.com', 'www.pinterest.com',
            'tumblr.com', 'www.tumblr.com', 'mastodon.social', 'mastodon.online',
            
            # E-commerce & marketplaces
            'amazon.com', 'www.amazon.com', 'ebay.com', 'www.ebay.com',
            'walmart.com', 'www.walmart.com', 'target.com', 'www.target.com',
            'etsy.com', 'www.etsy.com', 'shopify.com', 'www.shopify.com',
            'aliexpress.com', 'www.aliexpress.com', 'alibaba.com', 'www.alibaba.com',
            'bestbuy.com', 'www.bestbuy.com', 'newegg.com', 'www.newegg.com',
            'homedepot.com', 'www.homedepot.com', 'lowes.com', 'www.lowes.com',
            'costco.com', 'www.costco.com', 'samsclub.com', 'www.samsclub.com',
            'wayfair.com', 'www.wayfair.com', 'ikea.com', 'www.ikea.com',
            
            # Tech companies & platforms
            'microsoft.com', 'www.microsoft.com', 'apple.com', 'www.apple.com',
            'github.com', 'www.github.com', 'gitlab.com', 'www.gitlab.com',
            'stackoverflow.com', 'www.stackoverflow.com', 'medium.com', 'www.medium.com',
            'bitbucket.org', 'www.bitbucket.org', 'sourceforge.net', 'www.sourceforge.net',
            'atlassian.com', 'www.atlassian.com', 'jira.com', 'www.jira.com',
            'notion.so', 'www.notion.so', 'trello.com', 'www.trello.com',
            'asana.com', 'www.asana.com', 'monday.com', 'www.monday.com',
            'zoom.us', 'www.zoom.us', 'teams.microsoft.com', 'meet.google.com',
            'webex.com', 'www.webex.com', 'gotomeeting.com', 'www.gotomeeting.com',
            
            # Banking & financial services
            'chase.com', 'www.chase.com', 'bankofamerica.com', 'www.bankofamerica.com',
            'wellsfargo.com', 'www.wellsfargo.com', 'paypal.com', 'www.paypal.com',
            'citibank.com', 'www.citibank.com', 'usbank.com', 'www.usbank.com',
            'capitalone.com', 'www.capitalone.com', 'discover.com', 'www.discover.com',
            'americanexpress.com', 'www.americanexpress.com', 'venmo.com', 'www.venmo.com',
            'square.com', 'www.square.com', 'stripe.com', 'www.stripe.com',
            'coinbase.com', 'www.coinbase.com', 'kraken.com', 'www.kraken.com',
            'robinhood.com', 'www.robinhood.com', 'fidelity.com', 'www.fidelity.com',
            'schwab.com', 'www.schwab.com', 'etrade.com', 'www.etrade.com',
            'tdameritrade.com', 'www.tdameritrade.com', 'mint.com', 'www.mint.com',
            
            # Email providers
            'gmail.com', 'mail.google.com', 'outlook.com', 'www.outlook.com',
            'yahoo.com', 'mail.yahoo.com', 'protonmail.com', 'www.protonmail.com',
            'icloud.com', 'www.icloud.com', 'zoho.com', 'www.zoho.com',
            'aol.com', 'www.aol.com', 'yandex.ru', 'mail.ru',
            
            # Streaming & entertainment
            'netflix.com', 'www.netflix.com', 'youtube.com', 'www.youtube.com',
            'spotify.com', 'www.spotify.com', 'hulu.com', 'www.hulu.com',
            'disneyplus.com', 'www.disneyplus.com', 'hbomax.com', 'www.hbomax.com',
            'primevideo.com', 'www.primevideo.com', 'twitch.tv', 'www.twitch.tv',
            'soundcloud.com', 'www.soundcloud.com', 'pandora.com', 'www.pandora.com',
            'crunchyroll.com', 'www.crunchyroll.com', 'vimeo.com', 'www.vimeo.com',
            'dailymotion.com', 'www.dailymotion.com', 'peacocktv.com', 'www.peacocktv.com',
            
            # News & media
            'cnn.com', 'www.cnn.com', 'bbc.com', 'www.bbc.com', 'bbc.co.uk', 'www.bbc.co.uk',
            'nytimes.com', 'www.nytimes.com', 'reuters.com', 'www.reuters.com',
            'theguardian.com', 'www.theguardian.com', 'washingtonpost.com', 'www.washingtonpost.com',
            'wsj.com', 'www.wsj.com', 'forbes.com', 'www.forbes.com',
            'bloomberg.com', 'www.bloomberg.com', 'cnbc.com', 'www.cnbc.com',
            'npr.org', 'www.npr.org', 'apnews.com', 'www.apnews.com',
            'usatoday.com', 'www.usatoday.com', 'latimes.com', 'www.latimes.com',
            'time.com', 'www.time.com', 'newsweek.com', 'www.newsweek.com',
            
            # Cloud services & storage
            'dropbox.com', 'www.dropbox.com', 'drive.google.com', 'docs.google.com',
            'onedrive.live.com', 'onedrive.com', 'box.com', 'www.box.com',
            'mega.nz', 'www.mega.nz', 'sync.com', 'www.sync.com',
            'pcloud.com', 'www.pcloud.com', 'backblaze.com', 'www.backblaze.com',
            
            # Education & learning
            'wikipedia.org', 'www.wikipedia.org', 'coursera.org', 'www.coursera.org',
            'udemy.com', 'www.udemy.com', 'khanacademy.org', 'www.khanacademy.org',
            'edx.org', 'www.edx.org', 'linkedin.com', 'learning.linkedin.com',
            'skillshare.com', 'www.skillshare.com', 'pluralsight.com', 'www.pluralsight.com',
            'udacity.com', 'www.udacity.com', 'codecademy.com', 'www.codecademy.com',
            'duolingo.com', 'www.duolingo.com', 'quizlet.com', 'www.quizlet.com',
            
            # Government & official sites
            'irs.gov', 'www.irs.gov', 'usa.gov', 'www.usa.gov',
            'usps.com', 'www.usps.com', 'nasa.gov', 'www.nasa.gov',
            'cdc.gov', 'www.cdc.gov', 'nih.gov', 'www.nih.gov',
            'whitehouse.gov', 'www.whitehouse.gov', 'congress.gov', 'www.congress.gov',
            
            # Travel & booking
            'booking.com', 'www.booking.com', 'airbnb.com', 'www.airbnb.com',
            'expedia.com', 'www.expedia.com', 'hotels.com', 'www.hotels.com',
            'tripadvisor.com', 'www.tripadvisor.com', 'kayak.com', 'www.kayak.com',
            'priceline.com', 'www.priceline.com', 'uber.com', 'www.uber.com',
            'lyft.com', 'www.lyft.com', 'delta.com', 'www.delta.com',
            'united.com', 'www.united.com', 'southwest.com', 'www.southwest.com',
            
            # Gaming & entertainment
            'steam.com', 'store.steampowered.com', 'epicgames.com', 'www.epicgames.com',
            'playstation.com', 'www.playstation.com', 'xbox.com', 'www.xbox.com',
            'nintendo.com', 'www.nintendo.com', 'roblox.com', 'www.roblox.com',
            'minecraft.net', 'www.minecraft.net', 'blizzard.com', 'www.blizzard.com',
            'ea.com', 'www.ea.com', 'ubisoft.com', 'www.ubisoft.com',
            
            # Software & tools
            'adobe.com', 'www.adobe.com', 'office.com', 'www.office.com',
            'canva.com', 'www.canva.com', 'figma.com', 'www.figma.com',
            'notion.so', 'www.notion.so', 'evernote.com', 'www.evernote.com',
            'grammarly.com', 'www.grammarly.com', 'lastpass.com', 'www.lastpass.com',
            '1password.com', 'www.1password.com', 'dashlane.com', 'www.dashlane.com',
            'malwarebytes.com', 'www.malwarebytes.com', 'avast.com', 'www.avast.com',
            'avg.com', 'www.avg.com', 'norton.com', 'www.norton.com',
            'mcafee.com', 'www.mcafee.com', 'kaspersky.com', 'www.kaspersky.com',
            
            # Domain registrars & hosting
            'godaddy.com', 'www.godaddy.com', 'namecheap.com', 'www.namecheap.com',
            'bluehost.com', 'www.bluehost.com', 'hostgator.com', 'www.hostgator.com',
            'squarespace.com', 'www.squarespace.com', 'wix.com', 'www.wix.com',
            'wordpress.com', 'www.wordpress.com', 'wordpress.org', 'www.wordpress.org',
            
            # Developer tools & resources
            'npmjs.com', 'www.npmjs.com', 'pypi.org', 'www.pypi.org',
            'docker.com', 'www.docker.com', 'kubernetes.io', 'www.kubernetes.io',
            'jenkins.io', 'www.jenkins.io', 'terraform.io', 'www.terraform.io',
            'mongodb.com', 'www.mongodb.com', 'postgresql.org', 'www.postgresql.org',
            'mysql.com', 'www.mysql.com', 'redis.io', 'www.redis.io',
            
            # Major Universities (US)
            'harvard.edu', 'www.harvard.edu', 'mit.edu', 'www.mit.edu',
            'stanford.edu', 'www.stanford.edu', 'yale.edu', 'www.yale.edu',
            'princeton.edu', 'www.princeton.edu', 'columbia.edu', 'www.columbia.edu',
            'cornell.edu', 'www.cornell.edu', 'upenn.edu', 'www.upenn.edu',
            'berkeley.edu', 'www.berkeley.edu', 'caltech.edu', 'www.caltech.edu',
            'duke.edu', 'www.duke.edu', 'northwestern.edu', 'www.northwestern.edu',
            'uchicago.edu', 'www.uchicago.edu', 'jhu.edu', 'www.jhu.edu',
            'ucla.edu', 'www.ucla.edu', 'umich.edu', 'www.umich.edu',
            'nyu.edu', 'www.nyu.edu', 'georgetown.edu', 'www.georgetown.edu',
            
            # Major Universities (International)
            'ox.ac.uk', 'www.ox.ac.uk', 'cam.ac.uk', 'www.cam.ac.uk',
            'imperial.ac.uk', 'www.imperial.ac.uk', 'ucl.ac.uk', 'www.ucl.ac.uk',
            'ethz.ch', 'www.ethz.ch', 'utoronto.ca', 'www.utoronto.ca',
            'mcgill.ca', 'www.mcgill.ca', 'ubc.ca', 'www.ubc.ca',
            'nus.edu.sg', 'www.nus.edu.sg', 'ntu.edu.sg', 'www.ntu.edu.sg',
            'u-tokyo.ac.jp', 'www.u-tokyo.ac.jp', 'kyoto-u.ac.jp', 'www.kyoto-u.ac.jp',
            'anu.edu.au', 'www.anu.edu.au', 'sydney.edu.au', 'www.sydney.edu.au',
            
            # International Banks
            'hsbc.com', 'www.hsbc.com', 'barclays.co.uk', 'www.barclays.co.uk',
            'santander.com', 'www.santander.com', 'bnpparibas.com', 'www.bnpparibas.com',
            'deutschebank.com', 'www.deutschebank.com', 'credit-suisse.com', 'www.credit-suisse.com',
            'ubs.com', 'www.ubs.com', 'ing.com', 'www.ing.com',
            'societegenerale.com', 'www.societegenerale.com', 'commbank.com.au', 'www.commbank.com.au',
            'nab.com.au', 'www.nab.com.au', 'westpac.com.au', 'www.westpac.com.au',
            'rbc.com', 'www.rbc.com', 'td.com', 'www.td.com', 'bmo.com', 'www.bmo.com',
            'scotiabank.com', 'www.scotiabank.com', 'cibc.com', 'www.cibc.com',
            
            # Regional Banks (US)
            'pnc.com', 'www.pnc.com', 'suntrust.com', 'www.suntrust.com',
            'regions.com', 'www.regions.com', 'fifththird.com', 'www.fifththird.com',
            'key.com', 'www.key.com', 'bbt.com', 'www.bbt.com',
            'huntington.com', 'www.huntington.com', 'morganstanley.com', 'www.morganstanley.com',
            'goldmansachs.com', 'www.goldmansachs.com', 'jpmorgan.com', 'www.jpmorgan.com',
            
            # Insurance Companies
            'geico.com', 'www.geico.com', 'progressive.com', 'www.progressive.com',
            'statefarm.com', 'www.statefarm.com', 'allstate.com', 'www.allstate.com',
            'nationwide.com', 'www.nationwide.com', 'libertymutual.com', 'www.libertymutual.com',
            'travelers.com', 'www.travelers.com', 'metlife.com', 'www.metlife.com',
            'prudential.com', 'www.prudential.com', 'aig.com', 'www.aig.com',
            
            # Healthcare & Medical
            'mayoclinic.org', 'www.mayoclinic.org', 'clevelandclinic.org', 'www.clevelandclinic.org',
            'hopkinsmedicine.org', 'www.hopkinsmedicine.org', 'upmc.com', 'www.upmc.com',
            'kp.org', 'www.kp.org', 'ama-assn.org', 'www.ama-assn.org',
            'webmd.com', 'www.webmd.com', 'medlineplus.gov', 'www.medlineplus.gov',
            'drugs.com', 'www.drugs.com', 'rxlist.com', 'www.rxlist.com',
            
            # Professional Organizations
            'ieee.org', 'www.ieee.org', 'acm.org', 'www.acm.org',
            'aaas.org', 'www.aaas.org', 'apa.org', 'www.apa.org',
            'acs.org', 'www.acs.org', 'asme.org', 'www.asme.org',
            
            # International E-commerce
            'rakuten.com', 'www.rakuten.com', 'mercadolibre.com', 'www.mercadolibre.com',
            'flipkart.com', 'www.flipkart.com', 'jd.com', 'www.jd.com',
            'taobao.com', 'www.taobao.com', 'tmall.com', 'www.tmall.com',
            'lazada.com', 'www.lazada.com', 'shopee.com', 'www.shopee.com',
            
            # Food Delivery & Services
            'doordash.com', 'www.doordash.com', 'grubhub.com', 'www.grubhub.com',
            'ubereats.com', 'www.ubereats.com', 'postmates.com', 'www.postmates.com',
            'instacart.com', 'www.instacart.com', 'seamless.com', 'www.seamless.com',
            
            # Real Estate
            'zillow.com', 'www.zillow.com', 'trulia.com', 'www.trulia.com',
            'redfin.com', 'www.redfin.com', 'realtor.com', 'www.realtor.com',
            'apartments.com', 'www.apartments.com', 'rent.com', 'www.rent.com',
            
            # Job Boards
            'indeed.com', 'www.indeed.com', 'glassdoor.com', 'www.glassdoor.com',
            'monster.com', 'www.monster.com', 'careerbuilder.com', 'www.careerbuilder.com',
            'ziprecruiter.com', 'www.ziprecruiter.com', 'dice.com', 'www.dice.com',
            
            # Telecom Providers
            'verizon.com', 'www.verizon.com', 'att.com', 'www.att.com',
            'tmobile.com', 'www.tmobile.com', 'sprint.com', 'www.sprint.com',
            'comcast.com', 'www.comcast.com', 'xfinity.com', 'www.xfinity.com',
            'spectrum.com', 'www.spectrum.com', 'cox.com', 'www.cox.com',
            
            # Automotive
            'toyota.com', 'www.toyota.com', 'ford.com', 'www.ford.com',
            'honda.com', 'www.honda.com', 'chevrolet.com', 'www.chevrolet.com',
            'nissan.com', 'www.nissan.com', 'bmw.com', 'www.bmw.com',
            'mercedes-benz.com', 'www.mercedes-benz.com', 'tesla.com', 'www.tesla.com',
            'audi.com', 'www.audi.com', 'volkswagen.com', 'www.volkswagen.com',
            
            # Retail & Department Stores
            'macys.com', 'www.macys.com', 'nordstrom.com', 'www.nordstrom.com',
            'kohls.com', 'www.kohls.com', 'jcpenney.com', 'www.jcpenney.com',
            'sears.com', 'www.sears.com', 'tjmaxx.com', 'www.tjmaxx.com',
            'marshalls.com', 'www.marshalls.com', 'gap.com', 'www.gap.com',
            'oldnavy.com', 'www.oldnavy.com', 'zara.com', 'www.zara.com',
            'hm.com', 'www.hm.com', 'uniqlo.com', 'www.uniqlo.com',
        }
        
        # Add subdomains variations - matches any subdomain of these trusted domains
        self.legitimate_domain_roots = {
            # Major tech companies
            'google.', 'microsoft.', 'apple.', 'amazon.', 'meta.', 'facebook.',
            'alphabet.', 'ibm.', 'oracle.', 'salesforce.', 'sap.',
            
            # Social & communication
            'twitter.', 'linkedin.', 'instagram.', 'whatsapp.', 'telegram.',
            'discord.', 'slack.', 'zoom.', 'teams.', 'meet.', 'snapchat.',
            
            # Developer platforms
            'github.', 'gitlab.', 'bitbucket.', 'stackoverflow.', 'npmjs.',
            'docker.', 'kubernetes.', 'atlassian.', 'jenkins.', 'circleci.',
            
            # Cloud & storage
            'dropbox.', 'box.', 'mega.', 'icloud.', 'drive.', 'onedrive.',
            'aws.', 'azure.', 'cloudflare.', 'digitalocean.', 'linode.',
            
            # Streaming & media
            'youtube.', 'netflix.', 'spotify.', 'twitch.', 'soundcloud.',
            'hulu.', 'disney.', 'hbo.', 'pandora.', 'vimeo.',
            
            # E-commerce
            'ebay.', 'walmart.', 'target.', 'etsy.', 'shopify.',
            'aliexpress.', 'alibaba.', 'bestbuy.', 'newegg.', 'wayfair.',
            
            # Banking & finance
            'paypal.', 'stripe.', 'square.', 'venmo.', 'coinbase.',
            'chase.', 'wellsfargo.', 'bankofamerica.', 'citibank.',
            'capitalone.', 'discover.', 'americanexpress.', 'fidelity.',
            
            # Email & productivity
            'gmail.', 'outlook.', 'yahoo.', 'protonmail.', 'zoho.',
            'office.', 'notion.', 'evernote.', 'trello.', 'asana.',
            
            # News & media
            'cnn.', 'bbc.', 'reuters.', 'nytimes.', 'washingtonpost.',
            'forbes.', 'bloomberg.', 'wsj.', 'theguardian.', 'npr.',
            
            # Education
            'wikipedia.', 'coursera.', 'udemy.', 'khanacademy.', 'edx.',
            'codecademy.', 'duolingo.', 'skillshare.', 'pluralsight.',
            
            # Search engines
            'bing.', 'duckduckgo.', 'yandex.', 'baidu.', 'brave.',
            
            # Software & security
            'adobe.', 'canva.', 'figma.', 'grammarly.', 'lastpass.',
            '1password.', 'dashlane.', 'norton.', 'mcafee.', 'avast.',
            'malwarebytes.', 'kaspersky.', 'bitdefender.',
            
            # Gaming
            'steam.', 'epicgames.', 'playstation.', 'xbox.', 'nintendo.',
            'roblox.', 'minecraft.', 'blizzard.', 'ea.', 'ubisoft.',
            
            # Travel & booking
            'booking.', 'airbnb.', 'expedia.', 'hotels.', 'tripadvisor.',
            'uber.', 'lyft.', 'delta.', 'united.', 'southwest.',
            
            # Hosting & domains
            'godaddy.', 'namecheap.', 'bluehost.', 'hostgator.',
            'squarespace.', 'wix.', 'wordpress.',
            
            # Government (.gov domains are generally safe)
            'irs.gov', 'usa.gov', 'nasa.gov', 'cdc.gov', 'nih.gov',
            
            # Universities
            'harvard.', 'mit.', 'stanford.', 'yale.', 'princeton.',
            'columbia.', 'cornell.', 'upenn.', 'berkeley.', 'caltech.',
            'oxford.', 'cambridge.', 'imperial.', 'ucl.', 'ethz.',
            
            # International banks
            'hsbc.', 'barclays.', 'santander.', 'bnpparibas.', 'deutschebank.',
            'ubs.', 'ing.', 'rbc.', 'td.', 'bmo.', 'scotiabank.',
            
            # Insurance
            'geico.', 'progressive.', 'statefarm.', 'allstate.', 'nationwide.',
            
            # Healthcare
            'mayoclinic.', 'clevelandclinic.', 'hopkinsmedicine.', 'webmd.',
            
            # Automotive
            'toyota.', 'ford.', 'honda.', 'tesla.', 'bmw.', 'mercedes-benz.',
            
            # Telecom
            'verizon.', 'att.', 'tmobile.', 'comcast.', 'xfinity.', 'spectrum.',
        }
        
    def is_whitelisted(self, domain):
        """
        Check if domain is in the whitelist of legitimate sites.
        Must properly handle:
        - google.com -> TRUE
        - mail.google.com -> TRUE  
        - google.com.fake.tk -> FALSE (fake domain!)
        - paypal.com.phishing.tk -> FALSE (fake domain!)
        """
        # Direct match
        if domain in self.legitimate_domains:
            return True
        
        # Check for educational domains (.edu and international variants)
        # These are generally safe as .edu registration is restricted
        educational_patterns = [
            '.edu',           # US higher education
            '.edu.au',        # Australian education
            '.edu.sg',        # Singapore education
            '.edu.ph',        # Philippines education
            '.edu.my',        # Malaysia education
            '.ac.uk',         # UK academic institutions
            '.ac.nz',         # New Zealand academic
            '.ac.za',         # South Africa academic
            '.ac.jp',         # Japan academic
            '.ac.kr',         # South Korea academic
            '.ac.in',         # India academic
            '.edu.cn',        # China education
            '.edu.hk',        # Hong Kong education
            '.edu.tw',        # Taiwan education
            '.k12.us',        # US K-12 schools (state-specific)
            '.edu.mx',        # Mexico education
            '.edu.br',        # Brazil education
            '.edu.ar',        # Argentina education
            '.ac.id',         # Indonesia academic
            '.ac.th',         # Thailand academic
        ]
        
        # Check if domain ends with any educational pattern
        for pattern in educational_patterns:
            if domain.endswith(pattern):
                return True
        
        # Check if it's a subdomain of a legitimate root
        # Key insight: The whitelisted root must be the BASE domain (SLD + TLD),
        # not just appear anywhere in the full domain
        for root in self.legitimate_domain_roots:
            # Root is like 'google.' or 'github.' - check if domain is subdomain
            if root.endswith('.'):
                root_without_dot = root.rstrip('.')
                
                # Split domain into parts
                parts = domain.split('.')
                
                # We need to check if root is the second-level domain
                # For 'mail.google.com': parts = ['mail', 'google', 'com']
                # For 'google.com.fake.tk': parts = ['google', 'com', 'fake', 'tk']
                
                # The legitimate base domain should be in positions [-2] (SLD)
                # e.g., google.com has 'google' at parts[-2]
                # mail.google.com has 'google' at parts[-2]
                # google.com.fake.tk has 'fake' at parts[-2] (NOT google!)
                
                if len(parts) >= 2:
                    # Check if the second-level domain matches our root
                    if parts[-2] == root_without_dot:
                        return True
                    
                    # Also handle subdomains: mail.google.com
                    # In this case, google is at parts[-2], which we already checked
                
            else:
                # Root doesn't end with dot - exact match check (like 'irs.gov')
                if domain == root or domain.endswith('.' + root):
                    return True
        
        return False
    
    def extract_all_features(self, url):
        """Extract all features from a URL"""
        features = {}
        
        # Basic validation
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        parsed = urlparse(url)
        
        # Check whitelist first
        features['is_whitelisted'] = self.is_whitelisted(parsed.netloc)
        
        # Basic features
        features.update(self._extract_basic_features(url, parsed))
        
        # Lexical features
        features.update(self._extract_lexical_features(url, parsed))
        
        # Domain features
        features.update(self._extract_domain_features(parsed.netloc, features['is_whitelisted']))
        
        # Security features
        features.update(self._extract_security_features(url, parsed))
        
        return features
    
    def _extract_basic_features(self, url, parsed):
        """Extract basic URL features"""
        return {
            'url': url,
            'domain': parsed.netloc,
            'scheme': parsed.scheme,
            'path': parsed.path,
            'query': parsed.query,
            'is_https': parsed.scheme == 'https'
        }
    
    def _extract_lexical_features(self, url, parsed):
        """Extract lexical/syntactic features"""
        features = {}
        
        # URL length features
        features['url_length'] = len(url)
        features['domain_length'] = len(parsed.netloc)
        features['path_length'] = len(parsed.path)
        features['query_length'] = len(parsed.query)
        
        # Character count features
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_underscores'] = url.count('_')
        features['num_slashes'] = url.count('/')
        features['num_question_marks'] = url.count('?')
        features['num_equal_signs'] = url.count('=')
        features['num_at_symbols'] = url.count('@')
        features['num_ampersands'] = url.count('&')
        features['num_digits'] = sum(c.isdigit() for c in url)
        
        # Special character ratio
        special_chars = sum(not c.isalnum() for c in url)
        features['special_char_ratio'] = special_chars / len(url) if len(url) > 0 else 0
        
        # Subdomain analysis
        domain_parts = parsed.netloc.split('.')
        features['num_subdomains'] = max(0, len(domain_parts) - 2)
        features['has_multiple_subdomains'] = len(domain_parts) > 3
        
        # IP address detection
        features['has_ip_address'] = bool(re.search(r'\d+\.\d+\.\d+\.\d+', parsed.netloc))
        
        # Port detection
        features['has_port'] = ':' in parsed.netloc and not parsed.scheme in parsed.netloc
        
        # Suspicious patterns
        features['has_suspicious_tld'] = any(tld in parsed.netloc for tld in self.suspicious_tlds)
        features['is_url_shortener'] = any(domain in parsed.netloc for domain in self.shortener_domains)
        
        # Keyword detection
        features['num_phishing_keywords'] = sum(
            keyword in url.lower() for keyword in self.phishing_keywords
        )
        features['has_login_keywords'] = bool(
            re.search(r'(login|verify|account|secure|update|confirm)', url.lower())
        )
        
        # Entropy calculation (randomness of URL)
        features['url_entropy'] = self._calculate_entropy(url)
        
        return features
    
    def _extract_domain_features(self, domain, is_whitelisted=False):
        """Extract domain-related features"""
        features = {}
        
        # If whitelisted, assume it's a well-established, legitimate domain
        if is_whitelisted:
            features['domain_age_days'] = 7300  # ~20 years (very old, trusted)
            features['domain_age_months'] = 240
            features['is_new_domain'] = False
            features['has_registrar'] = True
            features['has_mx_record'] = True
            return features
        
        try:
            # WHOIS lookup for domain age
            domain_info = whois.whois(domain)
            
            if domain_info.creation_date:
                if isinstance(domain_info.creation_date, list):
                    creation_date = domain_info.creation_date[0]
                else:
                    creation_date = domain_info.creation_date
                
                domain_age_days = (datetime.now() - creation_date).days
                features['domain_age_days'] = domain_age_days
                features['domain_age_months'] = domain_age_days / 30
                features['is_new_domain'] = domain_age_days < 365  # Less than 1 year
            else:
                features['domain_age_days'] = -1
                features['domain_age_months'] = -1
                features['is_new_domain'] = True
                
            # Domain registration info
            features['has_registrar'] = bool(domain_info.registrar)
            
        except Exception as e:
            # WHOIS lookup failed (domain may not exist or be private)
            features['domain_age_days'] = -1
            features['domain_age_months'] = -1
            features['is_new_domain'] = True
            features['has_registrar'] = False
        
        # DNS records check
        features['has_mx_record'] = self._check_mx_record(domain)
        
        return features
    
    def _extract_security_features(self, url, parsed):
        """Extract security-related features"""
        features = {}
        
        # SSL certificate check
        if parsed.scheme == 'https':
            cert_info = self._check_ssl_certificate(parsed.netloc)
            features.update(cert_info)
        else:
            features['has_valid_ssl'] = False
            features['ssl_issuer'] = None
            features['ssl_days_until_expiry'] = -1
        
        # Redirect detection
        features['has_redirect_symbols'] = '//' in parsed.path
        
        # Obfuscation detection
        features['has_hex_encoding'] = bool(re.search(r'%[0-9a-fA-F]{2}', url))
        features['has_punycode'] = 'xn--' in parsed.netloc
        
        return features
    
    def _calculate_entropy(self, text):
        """Calculate Shannon entropy of text"""
        from collections import Counter
        import math
        
        if not text:
            return 0
        
        counter = Counter(text)
        length = len(text)
        entropy = -sum(
            (count / length) * math.log2(count / length)
            for count in counter.values()
        )
        return round(entropy, 4)
    
    def _check_ssl_certificate(self, domain):
        """Check SSL certificate validity"""
        try:
            # Remove port if present
            hostname = domain.split(':')[0]
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiry
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.now()).days
                    
                    return {
                        'has_valid_ssl': True,
                        'ssl_issuer': cert.get('issuer', [[('organizationName', 'Unknown')]])[0][0][1],
                        'ssl_days_until_expiry': days_until_expiry
                    }
        except Exception:
            return {
                'has_valid_ssl': False,
                'ssl_issuer': None,
                'ssl_days_until_expiry': -1
            }
    
    def _check_mx_record(self, domain):
        """Check if domain has MX records (mail server)"""
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except Exception:
            return False
    
    def get_feature_vector(self, url):
        """
        Get numeric feature vector for ML model
        Returns a dictionary of numeric features only
        """
        all_features = self.extract_all_features(url)
        
        # Extract only numeric features for ML
        numeric_features = {
            'url_length': all_features['url_length'],
            'domain_length': all_features['domain_length'],
            'path_length': all_features['path_length'],
            'num_dots': all_features['num_dots'],
            'num_hyphens': all_features['num_hyphens'],
            'num_subdomains': all_features['num_subdomains'],
            'num_digits': all_features['num_digits'],
            'special_char_ratio': all_features['special_char_ratio'],
            'url_entropy': all_features['url_entropy'],
            'is_https': int(all_features['is_https']),
            'has_ip_address': int(all_features['has_ip_address']),
            'has_suspicious_tld': int(all_features['has_suspicious_tld']),
            'is_url_shortener': int(all_features['is_url_shortener']),
            'num_phishing_keywords': all_features['num_phishing_keywords'],
            'domain_age_days': all_features.get('domain_age_days', -1),
            'is_new_domain': int(all_features.get('is_new_domain', True)),
            'has_valid_ssl': int(all_features['has_valid_ssl']),
            'ssl_days_until_expiry': all_features['ssl_days_until_expiry'],
            'has_mx_record': int(all_features['has_mx_record']),
        }
        
        return numeric_features

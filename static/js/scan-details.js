/**
 * Additional scan details update function with enhanced analysis display
 */

function updateAdditionalDetails(data) {
    try {
        console.log('Updating additional details with enhanced analysis...');
        
        // URL Length
        const urlLengthEl = document.getElementById('urlLength');
        if (urlLengthEl && data.url_structure?.url_length) {
            urlLengthEl.textContent = data.url_structure.url_length + ' chars';
        }
        
        // Protocol Status
        const protocolEl = document.getElementById('protocolStatus');
        if (protocolEl && data.url_structure?.is_https !== undefined) {
            protocolEl.textContent = data.url_structure.is_https ? 'HTTPS ✓' : 'HTTP';
            protocolEl.style.color = data.url_structure.is_https ? '#10b981' : '#f59e0b';
        }
        
        // Subdomain Count
        const subdomainEl = document.getElementById('subdomainCount');
        if (subdomainEl && data.details?.num_subdomains !== undefined) {
            subdomainEl.textContent = data.details.num_subdomains;
        }
        
        // Detection Type
        const detectionTypeEl = document.getElementById('detectionType');
        if (detectionTypeEl && data.summary?.detection_method) {
            detectionTypeEl.textContent = data.summary.detection_method;
        }
        
        // Display enhanced analysis sections
        displayEnhancedAnalysis(data);
        
        console.log('✅ Additional details updated');
    } catch (error) {
        console.error('❌ Error updating additional details:', error);
    }
}

function displayEnhancedAnalysis(data) {
    // Find or create enhanced analysis container
    let enhancedContainer = document.getElementById('enhancedAnalysis');
    
    if (!enhancedContainer) {
        // Create container if it doesn't exist
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;
        
        enhancedContainer = document.createElement('div');
        enhancedContainer.id = 'enhancedAnalysis';
        enhancedContainer.style.cssText = `
            margin-top: 3rem;
            display: grid;
            gap: 1.5rem;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
            padding: 0 1rem;
        `;
        resultsSection.appendChild(enhancedContainer);
    }
    
    // Clear previous content
    enhancedContainer.innerHTML = '';
    
    // Build enhanced analysis HTML
    let html = '';
    
    // 1. Risk Assessment Card
    if (data.summary && data.risk_assessment) {
        const riskColor = data.risk_level === 'high' ? '#ef4444' : 
                         data.risk_level === 'medium' ? '#f59e0b' : '#10b981';
        
        html += `
            <div class="analysis-card" style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
                <h3 style="color: ${riskColor}; margin: 0 0 1rem 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 600;">
                    <i class="fas fa-exclamation-triangle"></i> Risk Assessment
                </h3>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">Risk Score</div>
                    <div style="font-size: 2rem; font-weight: 700; color: ${riskColor};">${data.risk_assessment.risk_score}/100</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">Threat Category</div>
                    <div style="font-size: 0.95rem; color: #fff; text-transform: capitalize;">${formatThreatCategory(data.risk_assessment.threat_category)}</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">Risk Description</div>
                    <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.9); line-height: 1.5;">${data.summary.risk_description || 'N/A'}</div>
                </div>
                <div style="background: rgba(0, 0, 0, 0.2); padding: 1rem; border-radius: 8px; border-left: 3px solid ${riskColor};">
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">Recommendation</div>
                    <div style="font-size: 0.95rem; color: #fff; font-weight: 500;">${data.summary.recommendation || 'N/A'}</div>
                </div>
            </div>
        `;
    }
    
    // 2. Risk & Trust Factors Card
    if (data.risk_assessment) {
        html += `
            <div class="analysis-card" style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
                <h3 style="color: #00d9ff; margin: 0 0 1rem 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 600;">
                    <i class="fas fa-list-check"></i> Detection Indicators
                </h3>
                <div style="display: flex; gap: 2rem; margin-bottom: 1.5rem;">
                    <div style="flex: 1;">
                        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">Risk Indicators</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #ef4444;">${data.risk_assessment.total_risk_indicators}</div>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">Trust Indicators</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #10b981;">${data.risk_assessment.total_trust_indicators}</div>
                    </div>
                </div>
                ${data.risk_assessment.risk_factors && data.risk_assessment.risk_factors.length > 0 ? `
                    <div style="margin-bottom: 1rem;">
                        <div style="font-size: 0.9rem; color: #ef4444; font-weight: 600; margin-bottom: 0.5rem;">🚨 Risk Factors:</div>
                        <ul style="margin: 0; padding-left: 1.2rem; color: rgba(255, 255, 255, 0.8); font-size: 0.85rem; line-height: 1.8;">
                            ${data.risk_assessment.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${data.risk_assessment.trust_factors && data.risk_assessment.trust_factors.length > 0 ? `
                    <div>
                        <div style="font-size: 0.9rem; color: #10b981; font-weight: 600; margin-bottom: 0.5rem;">✅ Trust Factors:</div>
                        <ul style="margin: 0; padding-left: 1.2rem; color: rgba(255, 255, 255, 0.8); font-size: 0.85rem; line-height: 1.8;">
                            ${data.risk_assessment.trust_factors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // 3. Technical Details Card
    if (data.technical_details) {
        const tech = data.technical_details;
        html += `
            <div class="analysis-card" style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
                <h3 style="color: #00d9ff; margin: 0 0 1rem 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 600;">
                    <i class="fas fa-cogs"></i> Technical Details
                </h3>
                ${tech.ssl_certificate ? `
                    <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">🔒 SSL Certificate</div>
                        <div style="font-size: 0.9rem; color: ${tech.ssl_certificate.has_valid_ssl ? '#10b981' : '#ef4444'}; font-weight: 500;">
                            ${tech.ssl_certificate.has_valid_ssl ? '✓ Valid' : '✗ Invalid/Missing'}
                        </div>
                        ${tech.ssl_certificate.ssl_issuer && tech.ssl_certificate.ssl_issuer !== 'Unknown' ? `
                            <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.7); margin-top: 0.3rem;">
                                Issuer: ${tech.ssl_certificate.ssl_issuer}
                            </div>
                        ` : ''}
                        ${tech.ssl_certificate.ssl_days_until_expiry > 0 ? `
                            <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.7); margin-top: 0.3rem;">
                                Expires in: ${tech.ssl_certificate.ssl_days_until_expiry} days
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                ${tech.dns_analysis ? `
                    <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">🌐 DNS Records</div>
                        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                            <div style="font-size: 0.85rem; color: ${tech.dns_analysis.has_dns_record ? '#10b981' : '#ef4444'};">
                                DNS: ${tech.dns_analysis.has_dns_record ? '✓' : '✗'}
                            </div>
                            <div style="font-size: 0.85rem; color: ${tech.dns_analysis.has_mx_record ? '#10b981' : '#f59e0b'};">
                                MX: ${tech.dns_analysis.has_mx_record ? '✓' : '✗'}
                            </div>
                        </div>
                    </div>
                ` : ''}
                ${tech.whois_information ? `
                    <div>
                        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">📋 WHOIS Data</div>
                        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.8);">
                            ${tech.whois_information.has_registrar ? '✓ Registered' : '✗ No Registrar'} • 
                            ${tech.whois_information.domain_age_days > 0 ? 
                                `${Math.floor(tech.whois_information.domain_age_days / 365)} years old` : 
                                'Age Unknown'}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // 4. Behavioral Indicators Card
    if (data.behavioral_indicators) {
        const behav = data.behavioral_indicators;
        html += `
            <div class="analysis-card" style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
                <h3 style="color: #00d9ff; margin: 0 0 1rem 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 600;">
                    <i class="fas fa-chart-line"></i> Behavioral Analysis
                </h3>
                <div style="display: grid; gap: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">URL Length</span>
                        <span style="font-size: 0.9rem; color: #fff; text-transform: capitalize;">${behav.url_length_category}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">Subdomain Depth</span>
                        <span style="font-size: 0.9rem; color: #fff;">${behav.subdomain_depth}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">Obfuscation</span>
                        <span style="font-size: 0.9rem; color: ${behav.obfuscation_detected ? '#ef4444' : '#10b981'};">
                            ${behav.obfuscation_detected ? '⚠️ Detected' : '✓ None'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">Redirect Potential</span>
                        <span style="font-size: 0.9rem; color: ${behav.redirect_potential ? '#ef4444' : '#10b981'};">
                            ${behav.redirect_potential ? '⚠️ Yes' : '✓ No'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6);">URL Shortener</span>
                        <span style="font-size: 0.9rem; color: ${behav.shortener_service ? '#f59e0b' : '#10b981'};">
                            ${behav.shortener_service ? '⚠️ Yes' : '✓ No'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // 5. External Verification Card
    if (data.external_verification && data.external_verification.verifiers_consulted && data.external_verification.verifiers_consulted.length > 0) {
        const ext = data.external_verification;
        html += `
            <div class="analysis-card" style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
                <h3 style="color: #00d9ff; margin: 0 0 1rem 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 600;">
                    <i class="fas fa-globe"></i> External Verification
                </h3>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">Sources Consulted</div>
                    <div style="font-size: 0.9rem; color: #fff;">${ext.verifiers_consulted.join(', ')}</div>
                </div>
                <div style="margin-bottom: 1rem;">
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">Consensus</div>
                    <div style="font-size: 0.9rem; color: #fff; text-transform: capitalize;">${ext.external_consensus.replace('_', ' ')}</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 0.5rem;">External Confidence</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #00d9ff;">${ext.confidence_from_external}%</div>
                </div>
            </div>
        `;
    }
    
    // Inject the HTML
    enhancedContainer.innerHTML = html;
    
    // Add fade-in animation
    setTimeout(() => {
        const cards = enhancedContainer.querySelectorAll('.analysis-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }, 100);
}

function formatThreatCategory(category) {
    const categories = {
        'legitimate': 'Legitimate Website',
        'credential_theft': 'Credential Theft Attack',
        'redirect_attack': 'Redirect/Shortener Attack',
        'direct_ip_phishing': 'Direct IP Phishing',
        'disposable_domain': 'Disposable Domain',
        'obfuscated_url': 'Obfuscated URL',
        'newly_registered_threat': 'Newly Registered Threat',
        'generic_phishing': 'Generic Phishing'
    };
    return categories[category] || category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

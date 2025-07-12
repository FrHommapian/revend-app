with open('templates/results.html', 'r') as f:
    content = f.read()

# Add the timing insights section after the pricing section
timing_section = '''
        <!-- Timing Insights Section -->
        {% if analysis_data.timing_insights %}
        <div class="card">
            <div class="card-header">
                <div class="card-title">⏰ Premium Timing Insights</div>
            </div>
            <div class="timing-insights-container">
                <!-- Optimal Timing -->
                <div class="timing-card timing-{{ analysis_data.timing_insights.optimal_timing.status }}">
                    <div class="timing-icon">🎯</div>
                    <div class="timing-content">
                        <h4>Optimal Timing</h4>
                        <p class="timing-message">{{ analysis_data.timing_insights.optimal_timing.message }}</p>
                        <p class="timing-action">{{ analysis_data.timing_insights.optimal_timing.action }}</p>
                    </div>
                </div>
                
                <!-- Seasonal Analysis -->
                <div class="timing-card timing-{{ analysis_data.timing_insights.seasonal_analysis.status }}">
                    <div class="timing-icon">📈</div>
                    <div class="timing-content">
                        <h4>Seasonal Trends</h4>
                        <p class="timing-message">{{ analysis_data.timing_insights.seasonal_analysis.message }}</p>
                        <p class="timing-tip">💡 {{ analysis_data.timing_insights.seasonal_analysis.tip }}</p>
                    </div>
                </div>
                
                <!-- Urgency Indicator -->
                <div class="timing-card timing-{{ analysis_data.timing_insights.urgency_indicator.level }}">
                    <div class="timing-icon">⚡</div>
                    <div class="timing-content">
                        <h4>Market Urgency</h4>
                        <p class="timing-message">{{ analysis_data.timing_insights.urgency_indicator.message }}</p>
                        <p class="timing-advice">📋 {{ analysis_data.timing_insights.urgency_indicator.advice }}</p>
                    </div>
                </div>
                
                <!-- Platform Timing -->
                <div class="timing-card timing-normal">
                    <div class="timing-icon">📱</div>
                    <div class="timing-content">
                        <h4>Platform Timing</h4>
                        <div class="platform-timing-list">
                            {% for platform, timing in analysis_data.timing_insights.platform_recommendations.items() %}
                            <p class="platform-timing">{{ timing }}</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <!-- Next Best Time -->
                <div class="timing-summary">
                    <h4>📅 Next Best Time to List</h4>
                    <p class="next-best-time">{{ analysis_data.timing_insights.next_best_time }}</p>
                </div>
            </div>
        </div>
        {% endif %}
        '''

# Insert after the pricing section
pricing_section_end = '''        </div>
        
        
                    <div class="row">'''

content = content.replace(pricing_section_end, '''        </div>
        ''' + timing_section + '''
        
                    <div class="row">''')

with open('templates/results.html', 'w') as f:
    f.write(content)

print("✅ Timing insights UI added!")

import datetime
import logging

logger = logging.getLogger(__name__)

class TimingInsights:
    def __init__(self):
        # Best selling times by category
        self.category_timing = {
            'electronics': {
                'best_days': ['Sunday', 'Monday', 'Tuesday'],
                'best_hours': '7-9 PM',
                'peak_months': ['November', 'December', 'January'],
                'seasonal_boost': 40,
                'reason': 'People research tech purchases on weekends and evenings'
            },
            'fashion_beauty': {
                'best_days': ['Friday', 'Saturday', 'Sunday'],
                'best_hours': '6-8 PM',
                'peak_months': ['March', 'April', 'September', 'October'],
                'seasonal_boost': 35,
                'reason': 'Fashion peaks during season transitions'
            },
            'vehicles': {
                'best_days': ['Saturday', 'Sunday'],
                'best_hours': '10 AM - 2 PM',
                'peak_months': ['March', 'April', 'September', 'October'],
                'seasonal_boost': 25,
                'reason': 'Weekend car shopping is traditional'
            },
            'home_garden': {
                'best_days': ['Saturday', 'Sunday'],
                'best_hours': '2-6 PM',
                'peak_months': ['March', 'April', 'May', 'September'],
                'seasonal_boost': 45,
                'reason': 'Home improvement peaks in spring and fall'
            },
            'baby_kids': {
                'best_days': ['Saturday', 'Sunday', 'Monday'],
                'best_hours': '8-10 AM, 2-4 PM',
                'peak_months': ['January', 'February', 'August', 'September'],
                'seasonal_boost': 30,
                'reason': 'Parents shop during nap times and back-to-school'
            }
        }
        
        # Platform-specific timing
        self.platform_timing = {
            'facebook': 'Sunday evenings (7-9 PM) - families browse together',
            'gumtree': 'Weekends (10 AM - 4 PM) - people have time for pickups',
            'ebay': 'Tuesday-Thursday (7-9 PM) - serious buyers research',
            'general': 'Weekend evenings (6-8 PM) - peak browsing time'
        }
    
    def get_timing_insights(self, category, brand, item_type, current_season=None):
        """Generate timing insights for a specific item"""
        try:
            # Get current time info
            now = datetime.datetime.now()
            current_day = now.strftime('%A')
            current_hour = now.hour
            current_month = now.strftime('%B')
            
            # Get category-specific timing
            timing_data = self.category_timing.get(category, self.category_timing['electronics'])
            
            # Generate insights
            insights = {
                'optimal_timing': self._get_optimal_timing(timing_data, current_day, current_hour),
                'seasonal_analysis': self._get_seasonal_analysis(timing_data, current_month),
                'platform_recommendations': self._get_platform_timing(),
                'urgency_indicator': self._get_urgency_indicator(timing_data, current_month),
                'next_best_time': self._get_next_best_time(timing_data, now)
            }
            
            logger.info(f"Generated timing insights for {category} - {brand} {item_type}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating timing insights: {e}")
            return self._get_default_insights()
    
    def _get_optimal_timing(self, timing_data, current_day, current_hour):
        """Determine optimal timing based on current time"""
        best_days = timing_data['best_days']
        best_hours = timing_data['best_hours']
        
        if current_day in best_days:
            if self._is_peak_hour(current_hour, best_hours):
                return {
                    'status': 'optimal',
                    'message': f"🔥 PERFECT TIME! {current_day} {best_hours} is peak selling time",
                    'action': 'List now for maximum visibility'
                }
            else:
                return {
                    'status': 'good',
                    'message': f"✅ Good day! Wait until {best_hours} for peak traffic",
                    'action': f'List today between {best_hours}'
                }
        else:
            next_best = self._get_next_best_day(best_days, current_day)
            return {
                'status': 'wait',
                'message': f"⏳ Consider waiting until {next_best} for better visibility",
                'action': f'Best results on {", ".join(best_days)}'
            }
    
    def _get_seasonal_analysis(self, timing_data, current_month):
        """Analyze seasonal trends"""
        peak_months = timing_data['peak_months']
        seasonal_boost = timing_data['seasonal_boost']
        
        if current_month in peak_months:
            return {
                'status': 'peak',
                'message': f"📈 PEAK SEASON! {current_month} demand is {seasonal_boost}% higher",
                'tip': 'Price confidently - buyers are actively searching'
            }
        elif self._is_near_peak_season(current_month, peak_months):
            return {
                'status': 'approaching',
                'message': f"📊 Demand increasing towards peak season",
                'tip': 'Consider waiting 2-3 weeks for peak demand'
            }
        else:
            return {
                'status': 'normal',
                'message': f"📅 Standard season - steady demand",
                'tip': f'Peak demand returns in {self._get_next_peak_month(peak_months)}'
            }
    
    def _get_platform_timing(self):
        """Get platform-specific timing recommendations"""
        return {
            'facebook': '📱 Facebook Marketplace: Sunday evenings (7-9 PM)',
            'gumtree': '🏠 Gumtree: Weekends (10 AM - 4 PM)',
            'ebay': '🛒 eBay: Tuesday-Thursday (7-9 PM)',
            'general': '🎯 General: Weekend evenings (6-8 PM)'
        }
    
    def _get_urgency_indicator(self, timing_data, current_month):
        """Determine urgency of listing"""
        if current_month in timing_data['peak_months']:
            return {
                'level': 'high',
                'message': '🚨 HIGH DEMAND PERIOD',
                'advice': 'List immediately to capitalize on peak season'
            }
        else:
            return {
                'level': 'normal',
                'message': '📊 NORMAL DEMAND',
                'advice': 'Wait for optimal timing for best results'
            }
    
    def _get_next_best_time(self, timing_data, now):
        """Calculate next optimal listing time"""
        best_days = timing_data['best_days']
        best_hours = timing_data['best_hours']
        
        # Simple next best time calculation
        if now.strftime('%A') in best_days:
            return f"Today at {best_hours}"
        else:
            next_day = self._get_next_best_day(best_days, now.strftime('%A'))
            return f"{next_day} at {best_hours}"
    
    def _is_peak_hour(self, current_hour, best_hours):
        """Check if current hour is in peak hours"""
        # Simple check for common patterns like "7-9 PM"
        if 'PM' in best_hours and '7-9' in best_hours:
            return 19 <= current_hour <= 21
        elif 'AM' in best_hours and '10' in best_hours:
            return 10 <= current_hour <= 14
        return False
    
    def _get_next_best_day(self, best_days, current_day):
        """Get next best day from current day"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_idx = days.index(current_day)
        
        for i in range(1, 8):
            next_day = days[(current_idx + i) % 7]
            if next_day in best_days:
                return next_day
        return best_days[0]
    
    def _is_near_peak_season(self, current_month, peak_months):
        """Check if current month is near peak season"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        current_idx = months.index(current_month)
        
        for peak_month in peak_months:
            peak_idx = months.index(peak_month)
            if abs(current_idx - peak_idx) <= 1:
                return True
        return False
    
    def _get_next_peak_month(self, peak_months):
        """Get next peak month"""
        return peak_months[0] if peak_months else "upcoming season"
    
    def _get_default_insights(self):
        """Return default insights if error occurs"""
        return {
            'optimal_timing': {
                'status': 'normal',
                'message': '📅 Weekend evenings are typically best for listings',
                'action': 'List on Saturday or Sunday between 6-8 PM'
            },
            'seasonal_analysis': {
                'status': 'normal',
                'message': '📊 Standard selling season',
                'tip': 'Monitor demand trends for optimal timing'
            },
            'platform_recommendations': {
                'general': '🎯 Weekend evenings work well for most platforms'
            },
            'urgency_indicator': {
                'level': 'normal',
                'message': '📊 NORMAL DEMAND',
                'advice': 'Time your listing for maximum visibility'
            },
            'next_best_time': 'This weekend evening'
        }

# Create global instance
timing_insights = TimingInsights()

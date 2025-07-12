with open('timing_insights.py', 'w') as f:
    f.write("""import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

def get_timing_insights(category, brand, item_type):
    \"\"\"Generate location and time-aware timing insights\"\"\"
    try:
        # Use Sydney timezone for Australian app
        sydney_tz = pytz.timezone('Australia/Sydney')
        now = datetime.datetime.now(sydney_tz)
        current_day = now.strftime('%A')
        current_hour = now.hour
        current_month = now.strftime('%B')
        current_month_num = now.month
        
        # Category-specific timing data
        category_data = {
            'electronics': {
                'best_days': ['Saturday', 'Sunday', 'Monday'],
                'best_hours': '7-9 PM',
                'peak_months': [11, 12, 1],  # Nov, Dec, Jan
                'reason': 'People research tech purchases on weekends and evenings'
            },
            'fashion_beauty': {
                'best_days': ['Friday', 'Saturday', 'Sunday'],
                'best_hours': '6-8 PM',
                'peak_months': [3, 4, 9, 10],  # Mar, Apr, Sep, Oct
                'reason': 'Fashion peaks during season transitions'
            },
            'vehicles': {
                'best_days': ['Saturday', 'Sunday'],
                'best_hours': '10 AM - 2 PM',
                'peak_months': [3, 4, 9, 10],
                'reason': 'Weekend car shopping is traditional'
            },
            'home_garden': {
                'best_days': ['Saturday', 'Sunday'],
                'best_hours': '2-6 PM',
                'peak_months': [3, 4, 5, 9],  # Spring and early autumn
                'reason': 'Home improvement peaks in spring and autumn'
            },
            'baby_kids': {
                'best_days': ['Saturday', 'Sunday', 'Monday'],
                'best_hours': '8-10 AM, 2-4 PM',
                'peak_months': [1, 2, 8, 9],  # New year and back to school
                'reason': 'Parents shop during quieter times'
            }
        }
        
        timing_data = category_data.get(category, category_data['electronics'])
        
        # Generate insights
        insights = {
            'optimal_timing': _get_optimal_timing(timing_data, current_day, current_hour, now),
            'seasonal_analysis': _get_seasonal_analysis(timing_data, current_month, current_month_num),
            'urgency_indicator': _get_urgency_indicator(timing_data, current_month_num),
            'platform_recommendations': _get_platform_timing(),
            'next_best_time': _get_next_best_time(timing_data, now)
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating timing insights: {e}")
        return _get_default_insights()

def _get_optimal_timing(timing_data, current_day, current_hour, now):
    \"\"\"Smart timing based on current Sydney time\"\"\"
    best_days = timing_data['best_days']
    best_hours = timing_data['best_hours']
    
    # Check if it's too late today
    if current_hour >= 22:  # After 10 PM
        next_day = _get_next_best_day(best_days, current_day)
        return {
            'status': 'wait',
            'message': f'🌙 Too late tonight - wait until {next_day}',
            'action': f'Best results on {next_day} between {best_hours}'
        }
    elif current_day in best_days and _is_peak_hour(current_hour, best_hours):
        return {
            'status': 'optimal',
            'message': f'🔥 Perfect time! {current_day} {best_hours} is peak selling time',
            'action': 'List now for maximum visibility'
        }
    elif current_day in best_days:
        return {
            'status': 'good',
            'message': f'✅ Good day! Peak hours are {best_hours}',
            'action': f'List this evening between {best_hours}'
        }
    else:
        next_best = _get_next_best_day(best_days, current_day)
        return {
            'status': 'wait',
            'message': f'⏳ Consider waiting until {next_best} for better visibility',
            'action': f'Best results on {", ".join(best_days[:2])}'
        }

def _get_seasonal_analysis(timing_data, current_month, current_month_num):
    \"\"\"Seasonal analysis for Australia\"\"\"
    peak_months = timing_data['peak_months']
    
    if current_month_num in peak_months:
        return {
            'status': 'peak',
            'message': f'📈 Peak season! {current_month} demand is higher',
            'tip': 'Great time to sell - buyers are actively searching'
        }
    else:
        # Find next peak month
        next_peak = None
        for month in peak_months:
            if month > current_month_num:
                next_peak = month
                break
        if not next_peak:
            next_peak = peak_months[0]  # Next year
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        return {
            'status': 'normal',
            'message': f'📅 Standard season - steady demand',
            'tip': f'Peak demand returns in {month_names[next_peak]}'
        }

def _get_urgency_indicator(timing_data, current_month_num):
    \"\"\"Market urgency based on season\"\"\"
    if current_month_num in timing_data['peak_months']:
        return {
            'level': 'high',
            'message': '🚨 High demand period',
            'advice': 'List soon to capitalize on peak season'
        }
    else:
        return {
            'level': 'normal',
            'message': '📊 Normal demand',
            'advice': 'Time your listing for optimal results'
        }

def _get_platform_timing():
    \"\"\"Platform-specific timing recommendations\"\"\"
    return {
        'facebook': '📱 Facebook Marketplace: Sunday evenings (7-9 PM)',
        'gumtree': '🏠 Gumtree: Weekend afternoons (2-6 PM)',
        'ebay': '🛒 eBay: Tuesday-Thursday (7-9 PM)',
        'general': '🎯 General: Weekend evenings (6-8 PM)'
    }

def _get_next_best_time(timing_data, now):
    \"\"\"Calculate next optimal listing time\"\"\"
    best_days = timing_data['best_days']
    best_hours = timing_data['best_hours']
    
    # If it's late, suggest next day
    if now.hour >= 22:
        next_day = _get_next_best_day(best_days, now.strftime('%A'))
        return f'{next_day} between {best_hours}'
    elif now.strftime('%A') in best_days:
        return f'This evening between {best_hours}'
    else:
        next_day = _get_next_best_day(best_days, now.strftime('%A'))
        return f'{next_day} between {best_hours}'

def _is_peak_hour(current_hour, best_hours):
    \"\"\"Check if current hour is in peak hours\"\"\"
    if '7-9 PM' in best_hours:
        return 19 <= current_hour <= 21
    elif '10 AM - 2 PM' in best_hours:
        return 10 <= current_hour <= 14
    elif '6-8 PM' in best_hours:
        return 18 <= current_hour <= 20
    elif '2-6 PM' in best_hours:
        return 14 <= current_hour <= 18
    return False

def _get_next_best_day(best_days, current_day):
    \"\"\"Get next best day from current day\"\"\"
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_idx = days.index(current_day)
    
    for i in range(1, 8):
        next_day = days[(current_idx + i) % 7]
        if next_day in best_days:
            return next_day
    return best_days[0]

def _get_default_insights():
    \"\"\"Default insights if error occurs\"\"\"
    return {
        'optimal_timing': {
            'status': 'normal',
            'message': '📅 Weekend evenings are typically best for listings',
            'action': 'Consider listing on Saturday or Sunday evening'
        },
        'seasonal_analysis': {
            'status': 'normal',
            'message': '📊 Standard selling season',
            'tip': 'Monitor trends for optimal timing'
        },
        'urgency_indicator': {
            'level': 'normal',
            'message': '📊 Normal demand',
            'advice': 'Time your listing for maximum visibility'
        },
        'platform_recommendations': {
            'general': '🎯 Weekend evenings work well for most platforms'
        },
        'next_best_time': 'Weekend evening'
    }
""")

print("✅ Timing insights fixed with proper time/location awareness!")

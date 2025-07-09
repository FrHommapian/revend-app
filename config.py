import json
import os

CONFIG_FILE = "dashboard_settings.json"

# Enhanced default settings focused on electronics and bicycles
DEFAULT_SETTINGS = {
    "categories": ["electronics", "bicycles"],
    "min_price": 50,
    "max_price": 2000,
    "min_margin": 50,
    "include_free": False,
    "only_trending": False,
    "location": "Sydney, NSW, Australia",
    "radius": 25,
    "scan_interval": 300,
    "max_items_per_scan": 20,
    "high_value_threshold": 100,
    "notification_enabled": False,
    "auto_scan": False
}

# Telegram settings - DISABLED
TELEGRAM_TOKEN = ""  # DISABLED
TELEGRAM_CHAT_ID = ""  # DISABLED

def load_settings():
    """Load settings with enhanced error handling"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = {**DEFAULT_SETTINGS, **user_settings}
                
                # Ensure categories is always electronics and bicycles
                if "categories" not in settings or not settings["categories"]:
                    settings["categories"] = ["electronics", "bicycles"]
                
                return settings
        except Exception as e:
            print(f"⚠️ Error reading settings file: {e}")
            print("Using default settings...")
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to configuration file"""
    try:
        # Ensure we only save electronics and bicycles
        settings["categories"] = ["electronics", "bicycles"]
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Error saving settings: {e}")
        return False

# Load settings on import
settings = load_settings()

# Expose settings as module variables for backward compatibility
MIN_PRICE = settings["min_price"]
MAX_PRICE = settings["max_price"]
MIN_MARGIN = settings["min_margin"]
INCLUDE_FREE = settings["include_free"]
ONLY_TRENDING = settings["only_trending"]
CATEGORIES = settings["categories"]
LOCATION = settings["location"]
RADIUS = settings["radius"]

print(f"✅ Configuration loaded - Categories: {', '.join(settings['categories'])}")
print(f"💰 Price range: ${settings['min_price']} - ${settings['max_price']}")
print(f"📈 Minimum margin: ${settings['min_margin']}")
print(f"📍 Location: {settings['location']} ({settings['radius']}km radius)")
print(f"📱 Telegram notifications: {'✅ ENABLED' if TELEGRAM_TOKEN else '❌ DISABLED'}")

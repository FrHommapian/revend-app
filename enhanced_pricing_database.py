# Comprehensive pricing database for Australian market (2025)
ENHANCED_PRICING_DATABASE = {
    # MUSICAL INSTRUMENTS (Expanded)
    'roland_fp_series': {'brand': 'roland', 'keywords': ['fp-', 'fp30', 'fpx30', 'fp-x30', 'fp60', 'fp90'], 'base_price': 1200, 'range': (800, 1800), 'retail_price': 1799, 'category': 'musical'},
    'roland_juno': {'brand': 'roland', 'keywords': ['juno', 'synthesizer'], 'base_price': 800, 'range': (500, 1200), 'retail_price': 1299, 'category': 'musical'},
    'yamaha_p_series': {'brand': 'yamaha', 'keywords': ['p-45', 'p-125', 'p-515'], 'base_price': 1000, 'range': (600, 1600), 'retail_price': 1499, 'category': 'musical'},
    'yamaha_clavinova': {'brand': 'yamaha', 'keywords': ['clavinova', 'cvp'], 'base_price': 2500, 'range': (1500, 4000), 'retail_price': 4999, 'category': 'musical'},
    'gibson_guitar': {'brand': 'gibson', 'keywords': ['les paul', 'sg', 'guitar'], 'base_price': 1800, 'range': (1000, 3500), 'retail_price': 2999, 'category': 'musical'},
    'fender_guitar': {'brand': 'fender', 'keywords': ['stratocaster', 'telecaster', 'guitar'], 'base_price': 1200, 'range': (600, 2200), 'retail_price': 1899, 'category': 'musical'},
    'drums_acoustic': {'brand': 'any', 'keywords': ['drum kit', 'drums'], 'base_price': 800, 'range': (300, 1800), 'retail_price': 1299, 'category': 'musical'},
    
    # ELECTRONICS (Expanded)
    'apple_macbook_air_m1': {'brand': 'apple', 'keywords': ['macbook air m1'], 'base_price': 1200, 'range': (900, 1600), 'retail_price': 1999, 'category': 'electronics'},
    'apple_macbook_air_m2': {'brand': 'apple', 'keywords': ['macbook air m2'], 'base_price': 1500, 'range': (1200, 2000), 'retail_price': 2199, 'category': 'electronics'},
    'apple_macbook_pro_14': {'brand': 'apple', 'keywords': ['macbook pro 14'], 'base_price': 2200, 'range': (1800, 2800), 'retail_price': 2999, 'category': 'electronics'},
    'apple_iphone_15': {'brand': 'apple', 'keywords': ['iphone 15'], 'base_price': 1000, 'range': (800, 1300), 'retail_price': 1499, 'category': 'electronics'},
    'apple_iphone_14': {'brand': 'apple', 'keywords': ['iphone 14'], 'base_price': 800, 'range': (600, 1100), 'retail_price': 1399, 'category': 'electronics'},
    'apple_iphone_13': {'brand': 'apple', 'keywords': ['iphone 13'], 'base_price': 650, 'range': (450, 900), 'retail_price': 1199, 'category': 'electronics'},
    'samsung_galaxy_s24': {'brand': 'samsung', 'keywords': ['galaxy s24'], 'base_price': 800, 'range': (600, 1100), 'retail_price': 1199, 'category': 'electronics'},
    'samsung_galaxy_s23': {'brand': 'samsung', 'keywords': ['galaxy s23'], 'base_price': 650, 'range': (450, 900), 'retail_price': 999, 'category': 'electronics'},
    'nintendo_switch': {'brand': 'nintendo', 'keywords': ['switch console'], 'base_price': 350, 'range': (250, 450), 'retail_price': 469, 'category': 'electronics'},
    'playstation_5': {'brand': 'sony', 'keywords': ['ps5', 'playstation 5'], 'base_price': 600, 'range': (500, 750), 'retail_price': 799, 'category': 'electronics'},
    'xbox_series_x': {'brand': 'microsoft', 'keywords': ['xbox series x'], 'base_price': 650, 'range': (550, 800), 'retail_price': 799, 'category': 'electronics'},
    
    # FASHION & LUXURY (Expanded)
    'prada_handbag': {'brand': 'prada', 'keywords': ['handbag', 'bag', 'purse', 'milano'], 'base_price': 450, 'range': (200, 800), 'retail_price': 800, 'category': 'fashion'},
    'gucci_handbag': {'brand': 'gucci', 'keywords': ['handbag', 'bag', 'purse'], 'base_price': 500, 'range': (250, 900), 'retail_price': 900, 'category': 'fashion'},
    'louis_vuitton_handbag': {'brand': 'louis', 'keywords': ['handbag', 'bag', 'purse'], 'base_price': 600, 'range': (300, 1200), 'retail_price': 1200, 'category': 'fashion'},
    'chanel_handbag': {'brand': 'chanel', 'keywords': ['handbag', 'bag', 'purse'], 'base_price': 700, 'range': (400, 1500), 'retail_price': 1500, 'category': 'fashion'},
    'hermes_handbag': {'brand': 'hermes', 'keywords': ['birkin', 'kelly', 'handbag'], 'base_price': 8000, 'range': (5000, 15000), 'retail_price': 12000, 'category': 'fashion'},
    'rolex_watch': {'brand': 'rolex', 'keywords': ['submariner', 'datejust', 'watch'], 'base_price': 8000, 'range': (5000, 20000), 'retail_price': 12000, 'category': 'fashion'},
    'omega_watch': {'brand': 'omega', 'keywords': ['speedmaster', 'seamaster', 'watch'], 'base_price': 3000, 'range': (1500, 6000), 'retail_price': 4500, 'category': 'fashion'},
    'nike_sneakers': {'brand': 'nike', 'keywords': ['air jordan', 'air max', 'sneakers'], 'base_price': 120, 'range': (60, 250), 'retail_price': 199, 'category': 'fashion'},
    'adidas_sneakers': {'brand': 'adidas', 'keywords': ['yeezy', 'ultraboost', 'sneakers'], 'base_price': 150, 'range': (80, 300), 'retail_price': 249, 'category': 'fashion'},
    
    # VEHICLES (New Category)
    'toyota_camry': {'brand': 'toyota', 'keywords': ['camry'], 'base_price': 25000, 'range': (15000, 40000), 'retail_price': 45000, 'category': 'vehicle'},
    'honda_civic': {'brand': 'honda', 'keywords': ['civic'], 'base_price': 22000, 'range': (12000, 35000), 'retail_price': 38000, 'category': 'vehicle'},
    'bmw_3_series': {'brand': 'bmw', 'keywords': ['3 series', '320i', '330i'], 'base_price': 35000, 'range': (20000, 55000), 'retail_price': 65000, 'category': 'vehicle'},
    'tesla_model_3': {'brand': 'tesla', 'keywords': ['model 3'], 'base_price': 45000, 'range': (30000, 65000), 'retail_price': 70000, 'category': 'vehicle'},
    'motorcycle_harley': {'brand': 'harley', 'keywords': ['davidson', 'motorcycle'], 'base_price': 15000, 'range': (8000, 25000), 'retail_price': 25000, 'category': 'vehicle'},
    
    # HOME & FURNITURE (Expanded)
    'ikea_sofa': {'brand': 'ikea', 'keywords': ['sofa', 'couch'], 'base_price': 300, 'range': (150, 500), 'retail_price': 499, 'category': 'furniture'},
    'west_elm_sofa': {'brand': 'west elm', 'keywords': ['sofa', 'couch'], 'base_price': 800, 'range': (400, 1200), 'retail_price': 1299, 'category': 'furniture'},
    'dining_table_wooden': {'brand': 'any', 'keywords': ['dining table', 'wooden table'], 'base_price': 400, 'range': (150, 800), 'retail_price': 699, 'category': 'furniture'},
    'office_chair_herman': {'brand': 'herman miller', 'keywords': ['aeron', 'office chair'], 'base_price': 800, 'range': (500, 1200), 'retail_price': 1299, 'category': 'furniture'},
    'mattress_king': {'brand': 'any', 'keywords': ['king mattress', 'mattress king'], 'base_price': 600, 'range': (300, 1000), 'retail_price': 999, 'category': 'furniture'},
    
    # APPLIANCES (New Category)
    'refrigerator': {'brand': 'any', 'keywords': ['fridge', 'refrigerator'], 'base_price': 800, 'range': (400, 1500), 'retail_price': 1299, 'category': 'appliance'},
    'washing_machine': {'brand': 'any', 'keywords': ['washing machine', 'washer'], 'base_price': 600, 'range': (300, 1000), 'retail_price': 899, 'category': 'appliance'},
    'dishwasher': {'brand': 'any', 'keywords': ['dishwasher'], 'base_price': 500, 'range': (250, 800), 'retail_price': 799, 'category': 'appliance'},
    'microwave': {'brand': 'any', 'keywords': ['microwave'], 'base_price': 150, 'range': (50, 300), 'retail_price': 249, 'category': 'appliance'},
    
    # BABY & KIDS (Expanded)
    'baby_crib_wooden': {'brand': 'any', 'keywords': ['wooden crib', 'crib'], 'base_price': 250, 'range': (120, 500), 'retail_price': 449, 'category': 'baby'},
    'stroller_bugaboo': {'brand': 'bugaboo', 'keywords': ['stroller', 'pram'], 'base_price': 600, 'range': (300, 1000), 'retail_price': 999, 'category': 'baby'},
    'car_seat_britax': {'brand': 'britax', 'keywords': ['car seat'], 'base_price': 300, 'range': (150, 500), 'retail_price': 499, 'category': 'baby'},
    'high_chair': {'brand': 'any', 'keywords': ['high chair'], 'base_price': 150, 'range': (50, 300), 'retail_price': 249, 'category': 'baby'},
    
    # SPORTS & FITNESS (New Category)
    'peloton_bike': {'brand': 'peloton', 'keywords': ['bike', 'exercise bike'], 'base_price': 1800, 'range': (1200, 2500), 'retail_price': 2995, 'category': 'fitness'},
    'treadmill': {'brand': 'any', 'keywords': ['treadmill'], 'base_price': 800, 'range': (400, 1500), 'retail_price': 1299, 'category': 'fitness'},
    'golf_clubs': {'brand': 'any', 'keywords': ['golf clubs', 'golf set'], 'base_price': 500, 'range': (200, 1000), 'retail_price': 799, 'category': 'sports'},
    'bicycle_road': {'brand': 'any', 'keywords': ['road bike', 'bicycle'], 'base_price': 800, 'range': (300, 1500), 'retail_price': 1299, 'category': 'sports'},
    'surfboard': {'brand': 'any', 'keywords': ['surfboard'], 'base_price': 400, 'range': (150, 800), 'retail_price': 699, 'category': 'sports'},
    
    # COLLECTIBLES & ANTIQUES (New Category)
    'vintage_vinyl': {'brand': 'any', 'keywords': ['vinyl record', 'vinyl'], 'base_price': 25, 'range': (5, 100), 'retail_price': 35, 'category': 'collectible'},
    'pokemon_cards': {'brand': 'pokemon', 'keywords': ['pokemon cards', 'trading cards'], 'base_price': 50, 'range': (10, 500), 'retail_price': 100, 'category': 'collectible'},
    'vintage_camera': {'brand': 'any', 'keywords': ['vintage camera', 'film camera'], 'base_price': 200, 'range': (50, 800), 'retail_price': 400, 'category': 'collectible'},
    'antique_furniture': {'brand': 'any', 'keywords': ['antique'], 'base_price': 500, 'range': (100, 2000), 'retail_price': 1000, 'category': 'collectible'},
}

# Condition multipliers
CONDITION_MULTIPLIERS = {
    'excellent': 1.2,      # +20% for excellent condition
    'very_good': 1.0,      # Base price for very good
    'good': 0.85,          # -15% for good condition
    'fair': 0.65,          # -35% for fair condition
    'poor': 0.45           # -55% for poor condition
}

# Age depreciation rates (per year)
AGE_DEPRECIATION = {
    'electronics': 0.15,   # 15% per year
    'fashion': 0.20,       # 20% per year
    'vehicle': 0.12,       # 12% per year
    'furniture': 0.08,     # 8% per year
    'musical': 0.10,       # 10% per year
    'appliance': 0.12,     # 12% per year
    'baby': 0.25,          # 25% per year (high turnover)
    'fitness': 0.15,       # 15% per year
    'sports': 0.12,        # 12% per year
    'collectible': -0.05   # Appreciate 5% per year
}

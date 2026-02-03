import pandas as pd
import re
from pathlib import Path

DATA_DIR = Path("/workspaces/python/FYP/Data/Final/transactions.csv") 

OUT_FILE = "transactions_uncategorized.csv"

OUT_DIR = Path("/workspaces/python/FYP/Data/Final")

def categorize_transactions(file_path, output_file):
    df = pd.read_csv(file_path)

    def get_category(row):
        if str(row['category_id']).lower() != 'none':
            return row['category_id']
        
        merchant = str(row['merchant_name']).lower()
        description = str(row['description']).lower()
        text = f"{merchant} {description}"
        
        rules = {
            'Groceries': [
                r'tesco', r'sainsbury', r'lidl', r'aldi', r'walmart', r'milk', r'grocery', 
                r'supermarket', r'm&s', r'marks & spencer', r'co-op', r'spar', r'dunnes', 
                r'supervalu', r'garvey', r'gorillas', r'hellofresh', r'rookery mini market', r'marks & spence',
                r'mwrcadona', r'carrefour', r'asia market', r'supermercado'
            ],
            'Transportation': [
                r'uber', r'lyft', r'taxi', r'airlines', r'ryanair', r'united airlines', 
                r'delta', r'train', r'bus', r'flight', r'commute', r'leap card', r'car repair',
                r'bolt', r'rail', r'aircoach', r'metro', r'bus', r'national expres', r'airport',
                r'u express', r'aerobus', r'beauvais', r'sbb', r'flibco', r'metropolitan', r'rewe',
                r'freenow', r'airpo', r'airpor', r'port', r'tfi', r'metro'
            ],
            'Finance': [
                r'interest', r'intrst', r'transfer', r'payment', r'deposit', r'renteind', 
                r'fee', r'dividend', r'atm', r'credit card', r'cash', r'loan', r'savings', 
                r'pocket', r'salary', r'scholarship', r'capital one', r'hmrc', r'vault', 
                r'gusto pay', r'tectra', r'diamond insurance', r'budget insurance', r'american express',
                r'hm revenue and customs', r'ceramic tile company', r'moneybox', r'kensington mortgage company',
                r'vauxhall finance', r'autobank financial services', r'tradingview', r'youlend', r'wage day advance',
                r'pets and claws pet insurance', r'donati', r'idonate', r'roi ecomm', r'globale',
                r'bin ban teo', r'fbd', r'visa', r'tcard', r'trading', r'whydonate', r'airwallet',
                r'investment'
            ],
            'Fitness': [
                r'fitness', r'gym', r'yoga', r'swimming', r'climbing', r'sports', 
                r'workout', r'leisure centre', r'bicycle', r'bike', r'aquadome'
            ],
            'Shopping': [
                r'adidas', r'amazon', r'nike', r'store', r'clothing', r'fashion', r'mall', 
                r'gifts', r'flowers', r'apple', r'zara', r'h&m', r'ebay', r'pepco', 
                r'penney', r'tk maxx', r'wilko', r'cartridge', r'royal mail', r'shop', r'harrods', r'bupa',
                r'nutmeg', r'microsoft', r'klarna', r'monzo', r'king street brew house', r'pokerstars', r'burberry',
                r'primark', r'ikea', r'aliexpress', r'it tralee', r'shein', r'diesel', r'boozt', r'completesave',
                r'range', r'jysk', r'love and f', r'ardfert fuels', r'eurogiant', r'pha', r'stradivarius', r'pandora',
                r'eason', r'shell', r'the look', r'ksg', r'v13', r't k maxx', r'smyths toys', r'mr price',
                r'pewex', r'kiosk', r'365', r'tezenis', r'tienda', r'kiko', r'natural', r'corcho',
                r'citees', r'wh smith', r'trigo',r'jomidar', r'sephora', r'new yorker',r'focus',
                r'lacoste', r'asos', r'h & m', r'top oil croagh', r'zone street', r'marketpla', r'flowcomm',
                r'h m', r'pull and bear', r'national merch', r'bershka', r'louis and', r'shopping',
                r'paris', r'monoprix', r'parit', r'paul', r'lego', r'card world', r'temu', r'yesstyle',
                r'shoe suite', r'dealz', r'notino', r'the south pole', r'an post', r'tom', r'mr bell',
                r'best', r'stadtwerke', r'swisstaste', r'the alley', r'kirbys', r'vapecentric', r'shaws',
                r'smoke n vape', r'drivingtes', r'uno', r'finestr', r'deshoras', r'helados', r'churreria',
                r'stop and look', r'carrolls', r'duty free', r'marks & spence', r'polregio', r'circle k',
                r'linkedin', r'apple', r'superdrug', r'rituals', r'young adult', r'castle', r'byrnesworth', r'itunes',
                r'vape', r'delive', r'vapecentric', r'zoundindustrie', r'harvey norman', r'chargp', r'ticketmaster',
                r'beauty bay', r'sharlotte', r'next', r'fruugo', r'momo', r'heatons', r'iherb', r'ecolines',
                r'cigarettes', r'duty', r'sixsense', r'lookfantastic', r'makeup', r'charles', r'skz', r'il', r'bad',
                r'ups', r'mtu', r'tcard', r'photospecialist', r'supermac',r'university', r'foot locker' 
            ],
            'Food and Dining': [
                r'pizza', r'starbucks', r'mcdonald', r'kfc', r'pret', r'pica', r'restaurant', 
                r'cafe', r'bakery', r'takeway', r'dinner', r'burger', r'subway', r'eats', r'butlers', r'planet spice'
                r'star food and wine', r'last orders drink', r'nandos', r'alfies fish & chips', r'boscombe convenience', r'blasket',
                r'toogoodtog', r'north south', r'seanoc', r'ugly m', r'takara', r'aston quay', r'maddens', r'mercury',
                r'caffrey', r'costa', r'bar', r'mcdonalds', r'tapas', r'gracia', r'oaklands', r'coca cola', r'the coin off',
                r'pocha', r'brio', r'lana', r'pub', r'fress and good', r'coffe', r'off beat donut', r'akira', r'tamarind', 
                r'mercury',  r'butter', r'mr bells', r'hennessy', r'sakura', r'the daily grin', r'mc donald', r'luxury food',
                r'subway', r'off beat', r'food', r'coff', r'take away', r'bb', r'ever dish', r'nanas tea', r'spice',
                r'petit delice', r'wines', r'mizu', r'super asia', r'bread 41', r'bubblejoy', r'just eat', r'four star',
                r'mug', r'teas time', r'shaking lab', r'bramples', r'kyoto', r'fota', r'salty', r'krispy kreme', r'roundy',
                r'kiosco', r'rusticboow', r'insomnia', r'bean', r'the roast', r'curry', r'myprotein', r'fish', r'bewley', 
                r'maneki', r'thai', r'donuts', r'food', r'rustic', r'sushi', r'filter', r'white rabbit'
            ],
            'Housing and Utilities': [
                r'water bill', r'electricity', r'gas bill', r'bill', r'telecom', 
                r'internet', r'spark', r'utility', r'mobile', r'broadband', r'laundry', r'rent', r'electronic', r'kingshill cars',
                r'homeserve', r'bulb energy', r'home bargains', r'eir', r'electric', r'phone number', r'tralee town', r'supplies'
            ],
            'Medical/Dental': [
                r'pharmacy', r'doctor', r'hospital', r'medical', r'dentist', r'boots', 
                r'health', r'chemist', r'stobswell dental practice', r'nata dent', r'apteka',
                r'c.h.'
            ],
            'Entertainment': [
                r'arena', r'aquarium', r'cinema', r'theatre', r'movie', r'zoo', r'fun', 
                r'park', r'netflix', r'spotify', r'disney', r'music', r'bet365', 
                r'unibet', r'games', r'elemis spa', r'motorsport vision', r'northenden golf club', r'cambridge city council',
                r'museu', r'arbitrade', r'omniple', r'escape', r'entertainment', r'k-mart',
                r'gallery'
            ],
            'Travel': [
                r'hotel', r'holiday', r'airbnb', r'booking.com', r'travel', r'king street brew house', r'sky digital',
                r'zilch london', r'bookin', r'hosteleria', r'maldron', r'agoda', r'b&b'
            ],
            'Personal Hygiene': [
                r'toothpaste', r'shampoo', r'soap', r'salon', r'barber', r'nail co', r'mobi', r'top-up',
                r'expose beauty', r'fresha'
            ],
            'Hobbies': [
                r'crochet', r'knitting', r'craft', r'hobby', r'books'
            ]
        }
        
        for category, patterns in rules.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return category
                    
        return 'Other'

    df['category_id'] = df.apply(get_category, axis=1)

    df.to_csv(OUT_DIR / output_file, index=False)
    print(f"Categorization complete. File saved to: {output_file}")

categorize_transactions(DATA_DIR, OUT_FILE)
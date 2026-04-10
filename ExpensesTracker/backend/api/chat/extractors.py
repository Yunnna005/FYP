import re
from typing import Optional
from datetime import datetime, timedelta

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

CATEGORY_KEYWORDS = {
    "groceries": ["groceries", "grocery", "supermarket", "food shopping", "tesco", "sainsbury", "lidl", "aldi", "walmart", "milk", "grocery", 
                "supermarket", "m&s", "marks & spencer", "co-op", "spar", "dunnes", "supervalu", "garvey", "gorillas", "hellofresh", "rookery mini market", "marks & spence",
                "mwrcadona", "carrefour", "asia market", "supermercado"],
    "transportation": ["uber", "lyft", "taxi", "airlines", "ryanair", "united airlines", 
                "delta", "train", "bus", "flight", "commute", "leap card", "car repair",
                "bolt", "rail", "aircoach", "metro", "bus", "national expres", "airport",
                "u express", "aerobus", "beauvais", "sbb", "flibco", "metropolitan", "rewe",
                "freenow", "airpo", "airpor", "port", "tfi", "metro"],
    "finance": ["interest", "intrst", "transfer", "payment", "deposit", "renteind", 
                "fee", "dividend", "atm", "credit card", "cash", "loan", "savings", 
                "pocket", "salary", "scholarship", "capital one", "hmrc", "vault", 
                "gusto pay", "tectra", "diamond insurance", "budget insurance", "american express",
                "hm revenue and customs", "ceramic tile company", "moneybox", "kensington mortgage company",
                "vauxhall finance", "autobank financial services", "tradingview", "youlend", "wage day advance",
                "pets and claws pet insurance", "donati", "idontate", "roi ecomm", "globale",
                "bin ban teo", "fbd", "visa", "tcard", "trading", "whydonate", "airwallet",
                "investment"],
    "fitness": ["fitness", "gym", "yoga", "swimming", "climbing", "sports", 
                "workout", "leisure centre", "bicycle", "bike", "aquadome"],
    'shopping': ["adidas", "amazon", "nike", "store", "clothing", "fashion", "mall", 
                "gifts", "flowers", "apple", "zara", "h&m", "ebay", "pepco", 
                "penney", "tk maxx", "wilko", "cartridge", "royal mail", "shop", "harrods", "bupa",
                "nutmeg", "microsoft", "klarna", "monzo", "king street brew house", "pokerstars", "burberry",
                "primark", "ikea", "aliexpress", "it tralee", "shein", "diesel", "boozt", "completesave",
                "range", "jysk", "love and f", "ardfert fuels", "eurogiant", "pha", "stradivarius", "pandora",
                "eason", "shell", "the look", "ksg", "v13", "t k maxx", "smyths toys", "mr price",
                "pewex", "kiosk", "365", "tezenis", "tienda", "kiko", "natural", "corcho",
                "citees", "wh smith", "trigo","jomidar", "sephora", "new yorker","focus",
                "lacoste", "asos", "h & m", "top oil croagh", "zone street", "marketpla", "flowcomm",
                "h m", "pull and bear", "national merch", "bershka", "louis and", "shopping",
                "smoke n vape", "drivingtes", "uno", "finestr", "deshoras", "helados", "churreria",
                "stop and look", "carrolls", "duty free", "marks & spence", "polregio", "circle k",
                "linkedin", "apple", "superdrug", "rituals", "young adult", "castle", "byrnesworth", "itunes",
                "vape", "delive", "vapecentric", "zoundindustrie", "harvey norman", "chargp", "ticketmaster",
                "beauty bay", "sharlotte", "next", "fruugo", "momo", "heatons", "iherb", "ecolines",
                "cigarettes", "duty", "sixsense", "lookfantastic", "makeup", "charles", "skz", "il", "bad",
                "ups", "mtu", "tcard", "photospecialist", "supermac", "university", "foot locker"],
    'food and Dining': ["pizza", "starbucks", "mcdonald", "kfc", "pret", "pica", "restaurant", 
                "cafe", "bakery", "takeway", "dinner", "burger", "subway", "eats", "butlers", "planet spice",
                "star food and wine", "last orders drink", "nandos", "alfies fish & chips", "boscombe convenience", "blasket",
                "toogoodtog", "north south", "seanoc", "ugly m", "takara", "aston quay", "maddens", "mercury",
                "caffrey", "costa", "bar", "mcdonalds", "tapas", "gracia", "oaklands", "coca cola", "the coin off",
                "pocha", "brio", "lana", "pub", "fress and good", "coffe", "off beat donut", "akira", "tamarind", 
                "mercury",  "butter", "mr bells", "hennessy", "sakura", "the daily grin", "mc donald", "luxury food",
                "subway", "off beat", "food", "coff", "take away", "bb", "ever dish", "nanas tea", "spice",
                "petit delice", "wines", "mizu", "super asia", "bread 41", "bubblejoy", "just eat", "four star",
                "mug", "teas time", "shaking lab", "bramples", "kyoto", "fota", "salty", "krispy kreme", "roundy",
                "kiosco", "rusticboow", "insomnia", "bean", "the roast", "curry", "myprotein", "fish", "bewley", 
                "maneki", "thai", "donuts", "food", "rustic", "sushi", "filter", "white rabbit"],
    'housing and utilities': ["water bill", "electricity", "gas bill", "bill", "telecom", 
                "internet", "spark", "utility", "mobile", "broadband", "laundry", "rent", "electronic", "kingshill cars",
                "homeserve", "bulb energy", "home bargains", "eir", "electric", "phone number", "tralee town", "supplies"],
    'medical/dental': ["pharmacy", "doctor", "hospital", "medical", "dentist", "boots", 
                "health", "chemist", "stobswell dental practice", "nata dent", "apteka",
                "c.h.", "cork university hospital", "st patricks hospital", "st vincent's hospital", "mater hospital",
                "dental", "healthcare", "medicines", "prescription", "optical", "vision express", "eye care", "vision care"],
    'entertainment': ["arena", "aquarium", "cinema", "theatre", "movie", "zoo", "fun", 
                "park", "netflix", "spotfly", "disney", "music", "bet365", 
                "unibet", "games", "elemis spa", "motorsport vision", "northenden golf club", "cambridge city council",
                "museu", "arbitrade", "omniple", "escape", "entertainment", "k-mart",
                "gallery"],
    'travel': ["hotel", "holiday", "airbnb", "booking.com", "travel", "king street brew house", "sky digital",
                "zilch london", "bookin", "hosteleria", "maldron", "agoda", "b&b"],
    'personal hygiene': ["toothpaste", "shampoo", "soap", "salon", "barber", "nail co", "mobi", "top-up",
                "expose beauty", "fresha", "hair", "skincare", "personal care", "hygiene", "beauty", "wellness"],
    'hobbies': ["crochet", "knitting", "craft", "hobby", "books", "music", "art supplies", "gardening", "diy", "hobbies", "lego", "model building", "painting", "drawing"],
}


def extract_month(question: str) -> Optional[str]:
    q = question.lower()
    today = datetime.today()

    if "this month" in q:
        return today.strftime("%Y-%m")

    if "last month" in q or "previous month" in q:
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        return last_month.strftime("%Y-%m")

    for name, num in MONTH_NAMES.items():
        if name in q:
            year = today.year
            if num > today.month:
                year -= 1
            return f"{year}-{num:02d}"

    return None


def extract_category(question: str) -> Optional[str]:
    q = question.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return category
    return None
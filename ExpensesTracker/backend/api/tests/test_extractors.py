from api.chat.extractors import extract_month, extract_category
print(extract_month('how much did i spend last month'))
print(extract_month('spending in october'))
print(extract_category('how much on groceries'))
print(extract_category('rent payment'))
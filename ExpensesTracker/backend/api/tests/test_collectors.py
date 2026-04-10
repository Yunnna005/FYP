from api.chat.collectors import (
    get_latest_month, get_stats, get_recommendations, get_forecast,
    get_anomalies, get_flagged_transactions
)
import json

user = 'USR601Ie'
print('Latest Month:\n')
print(get_latest_month('USR601Ie'))
print('\nStats:\n')
print(json.dumps(get_stats(user), indent=2, default=str)[:500])
print('\nRecommendations:\n')
print(json.dumps(get_recommendations(user), indent=2, default=str)[:500])
print()
print('\nForecast:\n')
print(json.dumps(get_forecast(user), indent=2, default=str)[:500])
print()
print('\nAnomalies:\n')
print(json.dumps(get_anomalies(user), indent=2, default=str)[:500])
print()
print('\nFlagged Transactions:\n')
print(json.dumps(get_flagged_transactions(user), indent=2, default=str)[:500])
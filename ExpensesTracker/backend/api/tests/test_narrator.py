from api.chat.narrator import narrate

fake_context = {
    'stats': {
        'monthly': [{
            'month_start_date': '2026-03-01',
            'total_spent': -2400.50,
            'total_received': 4200.00,
            'spending_by_category': '{\"groceries\": 12, \"dining\": 8, \"rent\": 1}',
        }]
    }
}

answer = narrate('How much did I spend last month?', fake_context)
print(answer)
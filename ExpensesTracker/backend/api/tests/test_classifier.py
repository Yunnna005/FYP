from api.chat.classifier import classify

questions = [
    'How much did I spend on food this month?',
    'How much will I have at end of month?',
    'Anything weird in my spending?',
    'How can I save \$300 this month?',
    'Im traveling next month, how can I save extra \$500?',
    'How am I doing overall?',
]

for q in questions:
    intent = classify(q)
    print(f'{q}')
    print(f'  needs: {intent.needs}')
    print(f'  params: {intent.params}')
    print()
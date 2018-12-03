import random


def random_medical_news():
    first = [
        'Exercise', 'Stress', 'Fatty foods', 'Red wine', 'Daycare',
        'Computer terminals', 'Coffee', 'Smoking',
    ]
    second = [
        'depression', 'glaucoma', 'breast cancer', 'breast cancer',
        'hypothermia', 'a feeling of wellbeing', 'heart disease',
        'spontaneous remission', 'glaucoma',
    ]
    third = [
        'twins', 'rats', 'men 20-40', '7 out of 10 women',
        'arthritis suferrers', 'children', 'two-income families',
        'overweight smokers'
    ]

    return '{} can cause {} in {}!'.format(
        random.sample(first, 1)[0],
        random.sample(second, 1)[0],
        random.sample(third, 1)[0]
    )

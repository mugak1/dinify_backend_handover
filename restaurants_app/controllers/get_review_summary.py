from orders_app.models import Order


def get_review_summary(restaurant_id) -> dict:
    ratings = Order.objects.values('rating').filter(
        restaurant=restaurant_id
    ).exclude(rating__isnull=True)

    total_ratings = len(ratings)
    one_star = len([rating for rating in ratings if rating['rating'] == 1])
    two_star = len([rating for rating in ratings if rating['rating'] == 2])
    three_star = len([rating for rating in ratings if rating['rating'] == 3])
    four_star = len([rating for rating in ratings if rating['rating'] == 4])
    five_star = len([rating for rating in ratings if rating['rating'] == 5])

    one_star_percent = (one_star / total_ratings) * 100 if one_star > 0 and total_ratings > 0 else 0
    two_star_percent = (two_star / total_ratings) * 100 if two_star > 0 and total_ratings > 0 else 0
    three_star_percent = (three_star / total_ratings) * 100 if three_star > 0 and total_ratings > 0 else 0
    four_star_percent = (four_star / total_ratings) * 100 if four_star > 0 and total_ratings > 0 else 0
    five_star_percent = (five_star / total_ratings) * 100 if five_star > 0 and total_ratings > 0 else 0

    average_rating = sum([rating['rating'] for rating in ratings]) / total_ratings

    return {
        'total_ratings': total_ratings,
        'one_star_percent': one_star_percent,
        'two_star_percent': two_star_percent,
        'three_star_percent': three_star_percent,
        'four_star_percent': four_star_percent,
        'five_star_percent': five_star_percent,
        'average_rating': average_rating
    }

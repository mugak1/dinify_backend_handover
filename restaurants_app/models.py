"""
models for the restaurant app
"""
from django.db import models
from users_app.models import BaseModel, User


# Create your models here.
SUBSCRIPTION_CHOICES = (
    ('per_order', 'Per Order'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly')
)


class Restaurant(BaseModel):
    """
    the model for the restaurant
    """
    name = models.CharField(max_length=255, db_index=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    logo = models.ImageField(null=True, blank=True)
    cover_photo = models.ImageField(null=True, blank=True)
    status = models.CharField(max_length=255, default='pending')

    # dynamic configurations
    # if the orders should be prepaid before submission
    require_order_prepayments = models.BooleanField(default=False)
    # if to show ratings and reviews to the public
    expose_order_ratings = models.BooleanField(default=True)
    # if the restaurant allows deliveries
    allow_deliveries = models.BooleanField(default=False)
    # if the restaurant allows pickups
    allow_pickups = models.BooleanField(default=False)

    preferred_subscription_method = models.CharField(
        max_length=255,
        choices=SUBSCRIPTION_CHOICES,
        default='per_order'
    )
    order_surcharge_percentage = models.FloatField(default=1.0)
    flat_fee = models.FloatField(default=0.0)

    class Meta:
        """
        the metadata for the Restaurant model
        """
        db_table = 'restaurants'
        ordering = ['name']


class RestaurantEmployee(BaseModel):
    """
    the employees at the restaurant i.e. the waiters, chefs, etc
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    roles = models.JSONField(default=list)
    active = models.BooleanField(default=True)

    class Meta:
        """
        the metadata for the RestaurantEmployee model
        """
        db_table = 'restaurant_employees'
        ordering = ['restaurant', 'user__first_name']
        unique_together = ['user', 'restaurant']

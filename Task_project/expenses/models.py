from django.db import models

# Create your models here.

# expenses/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)

class Expense(models.Model):
    EQUAL = 'EQUAL'
    EXACT = 'EXACT'
    PERCENT = 'PERCENT'

    SPLIT_CHOICES = [
        (EQUAL, 'Equal'),
        (EXACT, 'Exact'),
        (PERCENT, 'Percent'),
    ]

    payer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='expenses_paid')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_type = models.CharField(max_length=10, choices=SPLIT_CHOICES)
    participants = models.ManyToManyField(UserProfile, related_name='expenses_participated')

    def __str__(self):
        return f"{self.payer.user.username} paid {self.amount} for {', '.join([p.user.username for p in self.participants.all()])}"


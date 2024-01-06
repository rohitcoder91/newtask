from django.contrib import admin
from .models import UserProfile,Expense

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Expense)


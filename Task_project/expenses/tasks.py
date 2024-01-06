# expenses/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.db.models import Sum
from .models import UserProfile


@shared_task
def send_expense_notification_email(expense_id):
    # Get the expense and participants
    expense = Expense.objects.get(id=expense_id)
    participants = expense.participants.all()

    # Calculate the total amount owed by each participant
    total_owed = expense.amount / participants.count()

    for participant in participants:
        # Send email to each participant
        subject = 'You have a new expense!'
        message = render_to_string('expense_notification_email.html', {'user': participant, 'total_owed': total_owed})
        plain_message = strip_tags(message)
        from_email = 'your_email@example.com'
        to_email = [participant.email]

        send_mail(subject, plain_message, from_email, to_email, html_message=message)

    return f"Expense notification emails sent successfully for Expense {expense_id}."

@shared_task
def send_weekly_balance_email():
    # Get all user profiles
    user_profiles = UserProfile.objects.all()

    for user in user_profiles:
        # Calculate the total amount owed to the user
        total_owed = user.expenses_participated.aggregate(Sum('amount'))['amount__sum'] or 0

        # Send email to the user
        subject = 'Weekly Balance Summary'
        message = render_to_string('weekly_balance_email.html', {'user': user, 'total_owed': total_owed})
        plain_message = strip_tags(message)
        from_email = 'your_email@example.com'
        to_email = [user.email]

        send_mail(subject, plain_message, from_email, to_email, html_message=message)

    return "Weekly balance summary emails sent successfully."


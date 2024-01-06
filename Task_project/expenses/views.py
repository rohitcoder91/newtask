from django.shortcuts import render

# Create your views here.

# expenses/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import UserProfile, Expense
from .serializers import UserProfileSerializer, ExpenseSerializer
from .tasks import send_expense_notification_email

@api_view(['POST'])
def add_expense(request):
    data = request.data
    payer_id = data.get('payer_id')
    amount = data.get('amount')
    split_type = data.get('split_type')
    participants_ids = data.get('participants_ids')

    try:
        payer = UserProfile.objects.get(id=payer_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "Payer not found"}, status=400)

    expense = Expense.objects.create(payer=payer, amount=amount, split_type=split_type)

    if split_type == Expense.EQUAL:
        total_participants = len(participants_ids)
        individual_share = amount / total_participants
        participants = UserProfile.objects.filter(id__in=participants_ids)
        expense.participants.set(participants)
        for participant in participants:
            participant.expenses_participated.add(expense)
            participant.save()
        payer.expenses_paid.add(expense)
        payer.save()

    elif split_type == Expense.EXACT:
        total_amount = sum(data.get('exact_amounts', []))
        if total_amount != amount:
            return Response({"error": "Total amounts do not match the expense amount"}, status=400)
        
        amounts_dict = dict(zip(participants_ids, data.get('exact_amounts')))
        participants = UserProfile.objects.filter(id__in=participants_ids)
        for participant in participants:
            if participant.id == payer_id:
                payer.expenses_paid.add(expense)
                payer.save()
            else:
                participant.expenses_participated.add(expense)
                participant.save()
            individual_share = amounts_dict.get(participant.id, 0)
            payer.expenses_paid.add(expense)
            payer.save()

    elif split_type == Expense.PERCENT:
        percentages = data.get('percentages', [])
        total_percentage = sum(percentages)
        if total_percentage != 100:
            return Response({"error": "Total percentage does not equal 100"}, status=400)

        participants = UserProfile.objects.filter(id__in=participants_ids)
        for index, participant in enumerate(participants):
            individual_share = (amount * percentages[index]) / 100
            payer.expenses_paid.add(expense)
            payer.save()
            participant.expenses_participated.add(expense)
            participant.save()
    # Trigger the email notification task asynchronously
    send_expense_notification_email.delay(expense.id)
    
    return Response({"message": "Expense added successfully"})


@api_view(['GET'])
def show_all_userbalances(request):
    user_profiles = UserProfile.objects.all()
    balances = {}

    for user in user_profiles:
        # Calculate the total amount paid by the user
        total_paid = user.expenses_paid.aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate the total amount owed to the user
        total_owed = user.expenses_participated.aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate the balance
        balance = total_paid - total_owed

        # Exclude users with zero balance
        if balance != 0:
            balances[user.id] = {
                "user": UserProfileSerializer(user).data,
                "balance": round(balance, 2)
            }

    return Response({"balances": balances})



@api_view(['GET'])
def show_balances(request, user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=400)

    balances = {}
    expenses_paid = user.expenses_paid.annotate(total_participants=Sum('participants')).distinct()
    
    for expense in expenses_paid:
        individual_share = expense.amount / expense.total_participants
        for participant in expense.participants.all():
            if participant != user:
                balances[participant.user.username] = balances.get(participant.user.username, 0) + individual_share

    expenses_participated = user.expenses_participated.annotate(total_participants=Sum('participants')).distinct()

    for expense in expenses_participated:
        individual_share = expense.amount / expense.total_participants
        balances[user.user.username] = balances.get(user.user.username, 0) - (individual_share * (expense.total_participants - 1))

    return Response({"balances": balances})

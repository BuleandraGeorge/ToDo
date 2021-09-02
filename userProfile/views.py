from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
from datetime import timedelta, datetime

from .models import profile, service, price, subscription
from goals.models import goal, task

### email 
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .utility_functions import email_setter

import stripe
import json
from django.http import JsonResponse
stripe.api_key=settings.STRIPE_SECRET_API_KEY

# Create your views here.
def userProfile(request):
    theProfile = get_object_or_404(profile, user__id=request.user.id)
    theSubscriptions = subscription.objects.filter(profile=theProfile)
    theServices = service.objects.all()
    form = PasswordChangeForm(request.user)
    cards=[]
    customerId=request.user.profile.stripe_id
    paymentMethods = stripe.PaymentMethod.list(
        customer=customerId,
        type='card'
    )
    for card in paymentMethods.data:
        cards.append(card)
    context={
            'profile':theProfile,
            'active_subscriptions': theSubscriptions,
            'services':theServices,
            'passForm':form,
            'card_data':cards,
            'timenow':timezone.now()
            }
    if request.method=="POST":
        pass_change_form = PasswordChangeForm(request.user, request.POST)
        if pass_change_form.is_valid():
            user = pass_change_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password was successfully updated!'))
        else:
            messages.error(request, _('Please correct the error below.'))
    template="userProfile/profile.html"
    return render(request, template, context)


def checkout(request):
    price_id = request.POST['price_id']
    the_service = get_object_or_404(service, price__id=price_id)
    the_price = get_object_or_404(price, pk=price_id)
    the_profile = request.user.profile
    if the_price.price_type=='l':
        payment = stripe.PaymentMethod.list(
            customer=the_profile.stripe_id,
            type='card'
        )
        if payment.data:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(the_price.amount*100),
                currency='gbp',
                confirm=True,
                customer=the_profile.stripe_id,
                payment_method=payment.data[0].id
            )
            if payment_intent.status=="success":
                sub=subscription(
                    service=the_service,
                    profile=the_profile,
                    price=the_price,
                    stripe_id=payment_intent.id,
                )
                sub_id=sub.save().id
                return redirect(reverse('success', args=[sub_id]))
        else:
            return redirect(reverse('payment_details'))
    db_sub = subscription(
        profile=the_profile,
        service=the_service,
        price=the_price,
        )
    db_sub.save()
    sub_id=db_sub.id
    return redirect(reverse('success', args=[sub_id]))

def update_subscription(request):
    sub_id = int(request.POST['sub_id'])
    price_id = int(request.POST['price_id'])
    sub=get_object_or_404(subscription, pk=sub_id)
    the_price = get_object_or_404(price, pk=price_id)
    payment = stripe.PaymentMethod.list(
        customer=sub.profile.stripe_id,
        type='card'
    )
    if payment.data:
        if the_price.price_type=='l':
            payment_intent = stripe.PaymentIntent.create(
                amount=int(the_price.amount*100),
                currency='gbp',
                confirm=True,
                customer=request.user.profile.stripe_id,
                payment_method=payment.data[0].id
            )
            if payment_intent.status=="success":
                sub=sub(
                    price=the_price,
                    stripe_id=payment_intent.id,
                )
        else:
            stripe.Subscription.modify(
                sub.stripe_id,
                default_payment_method=payment.data[0].id
            )
    else:
        return redirect(reverse('payment_details'))
    sub.price=the_price
    sub.save()
    sub_id=sub.id
    return redirect(reverse('success', args=[sub_id]))
#https://stripe.com/docs/billing/subscriptions/cancel
#trebuie sa creem o now view care se ocupa de reactivarea subscriptiilor cancelate
def reactivate_subscription(request):
    sub_id = request.POST['sub_id']
    price_id=request.POST['price_id']
    sub=get_object_or_404(subscription, pk=sub_id)
    the_price = get_object_or_404(price, pk=price_id)
    price_stripe_id=sub.price.stripe_id
    payment = stripe.PaymentMethod.list(
            customer=sub.profile.stripe_id,
            type='card'
    )
    if payment.data:
        stripe_sub=stripe.Subscription.create(
            customer=request.user.profile.stripe_id,
            items=[{
                'price':price_stripe_id
             }],
             default_payment_method=payment.data[0].id
        )
        sub.price.id=the_price.id,
        sub.stripe_id=stripe_sub.id
        sub.save()
    else:
        return redirect(reverse('payment_details'))
    return redirect(reverse('success', args=[sub_id]))

def subscription_success(request,sub_id):
    sub = get_object_or_404(subscription, pk=sub_id)
    context={
        'sub':sub
    }
    template="userProfile/success.html"
    return render(request, template, context)

def subscription_cancel(request,sub_id, now):
    sub = get_object_or_404(subscription, stripe_id=sub_id)
    if now:
        stripe.Subscription.delete(sub_id)
        sub.update(end_date=timezone.now())
    else:
        stripe.Subscription.modify(
            sub_id,
            cancel_at_period_end=True,
        )
    template="userProfile/cancel.html"
    context ={
        "sub": sub,
        "now": now,
    }
    return render(request, template, context)

def payment(request):
    setUpIntent = stripe.SetupIntent.create(
        payment_method_types=['card'],
        customer=request.user.profile.stripe_id,
    )
    client_secret = setUpIntent.client_secret
    publicKey = "pk_test_51JPUPSFrKFZJSdYm9qilHxr82f0igC2OHn4QkH1LXecNzIKjfmDZ4ZGKk6ofPkLmOmIfZ5Ddpfmd2pMgtq9rbr6S00mwTqikjZ"
    template="userProfile/update_payment_details.html"
    context={
        "public_key": publicKey,
        "client_secret":client_secret,
    }
    return render(request, template, context)

def delete_card(request, id_pm):
    stripe.PaymentMethod.detach(id_pm)
    return redirect(reverse('profile'))


@csrf_exempt
def webhook_received(request):
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    request_data = request.body

    if webhook_secret:
        signature = request.META['HTTP_STRIPE_SIGNATURE']
        try:
            event = stripe.Webhook.construct_event(
                payload=request.body, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']     
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'customer.subscription.trial_will_end':
        stripe_sub_id =data_object['subscription']
        try:
            the_sub = get_object_or_404(subscription, stripe_id=stripe_sub_id)
            email_setter(
            the_sub,
            "The trial for Goal Subscription will end soon",
            "userProfile/email_content/update_payment.txt"
            )
        except Exception as e:
            print(e)
            return redirect(reverse('goals'))
       

    if event_type == 'invoice.paid':
        stripe_sub_id =data_object['subscription']
        try:
            the_sub = get_object_or_404(subscription, stripe_id=stripe_sub_id)
            the_sub.save()
            email_setter(
            the_sub,
            "A word from the Achiever",
            "userProfile/email_content/subscription_success.txt"
            )
        except Exception as e:
            print(e)
        

    if event_type == 'setup_intent.succeeded':
        print("Method attached")


    if event_type == 'invoice.payment_failed':
        stripe_sub_id =data_object['subscription']
        try:
            the_sub = get_object_or_404(subscription, stripe_id=stripe_sub_id)
            email_setter(
            the_sub,
            "Payment failed, The Achiever",
            "userProfile/email_content/subscription_fail.txt"
            )
        except Exception as e:
            print(e)
       

    if event_type == 'customer.subscription.deleted':
        stripe_sub_id = data_object['subscription'] 
        try:
            the_sub = get_object_or_404(subscription, stripe_id=stripe_sub_id)
            email_setter(
            the_sub, 
            "Subscription Cancelled, The Achiever",
            "userProfile/email_content/subscription_cancelled.txt"
            )
        except Exception as e:
            print(e)
        
    print(event_type)
    return JsonResponse({'status': 'success'})
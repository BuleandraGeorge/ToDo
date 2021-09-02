from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def stripe_interval_getter(price_type):
    return 'month' if price_type=='m' else 'year'


def email_setter(subscription_object, subject, url_template):
    """ Sets everything for email """
    if subscription_object:
        period = 'Monthly' if subscription_object.price.price_type =='m' else 'Anually' if subscription_object.price.price_type =='a' else 'Life'
        total = subscription_object.price.amount
        context_data={
            'service_name':subscription_object.service.name, 
            'period':period,
            'total':total
        }
        customer_email = subscription_object.profile.user.email
    else:
        context_data={}
    body = render_to_string(url_template, context_data)
    DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject = subject,
        message=body,
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email]
    )
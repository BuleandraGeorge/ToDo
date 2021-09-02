from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta, datetime
import uuid
import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .utility_functions import stripe_interval_getter
stripe.api_key=settings.STRIPE_SECRET_API_KEY

class service(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=2000)
    stripe_id = models.CharField(max_length=256, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        product_data={
            'name':self.name,
            'description':self.description
        }
        if not self.stripe_id:
            stripe_service = stripe.Product.create(
                name=self.name,
                description=self.description
            )
            self.stripe_id=stripe_service.id
        else:
            stripe.Product.modify(
                self.stripe_id,
                product_data
            )
        super().save(*args, *kwargs)
        
    
    def __str__(self):
        return self.name


class price (models.Model):
    type_choices = [
        ('m',  'Montly Plan'),
        ('a',  'Annual Plan'),
        ('l','Life Plan')
        ]
    price_type = models.CharField( max_length=1, choices=type_choices)
    amount = models.DecimalField(decimal_places=2, max_digits=5)
    service=models.ForeignKey(service, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=256, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            if self.price_type!='l':
                stripe_price = stripe.Price.create(
                    unit_amount=int(self.amount *100),
                    currency='gbp',
                    product=self.service.stripe_id,
                    recurring={
                    'interval':stripe_interval_getter(self.price_type),
                    }
                )
            else:
                stripe_price = stripe.Price.create(
                    unit_amount=int(self.amount *100),
                    currency='gbp',
                    product=self.service.stripe_id,
                )
            self.stripe_id=stripe_price.id
        else:
            if self.price_type!='l':
                stripe_price = stripe.Price.modify(
                    self.stripe_id,
                    unit_amount=int(self.amount *100),
                    currency='gbp',
                    product=self.service.stripe_id,
                    recurring={
                    'interval':stripe_interval_getter(self.price_type),
                    }
                )
            else:
                stripe_price = stripe.Price.modify(
                    self.stripe_id,
                    unit_amount=int(self.amount *100),
                    currency='gbp',
                    product=self.service.stripe_id,
                )
        super().save(*args, *kwargs)

    def __str__(self):
        return self.get_price_type_display()


class profile(models.Model):
    active_subscriptions = models.ManyToManyField(
        service, 
        through='subscription', through_fields=('profile', 'service')
        )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=256, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_customer = stripe.Customer.create(
                email=self.user.email
            )
            self.stripe_id=stripe_customer.id
        super().save(*args, **kwargs)


    def __str__(self):
        return self.user.username

class subscription(models.Model):
    profile = models.ForeignKey(profile, on_delete=models.CASCADE)
    service = models.ForeignKey(service, on_delete=models.CASCADE)
    end_date=models.DateTimeField(blank=False, null=False, default=timezone.now)
    price=models.ForeignKey(price, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=256, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        if self.price.price_type!='l':
            if not self.stripe_id:
                sub = stripe.Subscription.create(
                    customer=self.profile.stripe_id,
                    items=[{
                        'price':self.price.stripe_id
                        }],
                    trial_period_days=30,
                )
                self.stripe_id=sub.id
            else:
                sub = stripe.Subscription.retrieve(self.stripe_id)
                if self.price.stripe_id!=sub['items']["data"][0].price.id:
                    stripe_sub=stripe.Subscription.modify(
                        self.stripe_id,
                        cancel_at_period_end=False,
                        proration_behavior='create_prorations',
                        items=[{
                            'id':sub['items']['data'][0].id,
                            'price':self.price.stripe_id
                            }]
                    )
                    sub=stripe_sub
            self.end_date=datetime.fromtimestamp(sub.current_period_end)
        else:
            if self.stripe_id:
                stripe_sub=stripe.Subscription.modify(
                        self.stripe_id,
                        cancel_at_period_end=True,
                )
            self.end_date="2100-01-01 00:00:00"
        super().save(*args, **kwargs)

    def __str__(self):
        sub_name = self.profile.user.username+" "+self.service.name+" "+ self.price.price_type
        return sub_name
        
    def return_time(self):
        if self.price.price_type=='m':
            return timedelta(days=30)
        elif self.price.price_type=="a":
            return timedelta(days=365)
        else:
            return timedelta(days=20000)

    def set_availability(self):
        self.start_date=timezone.now()
        if self.include_trial:
            self.end_date=self.return_time() + self.start_date + timedelta(days=30)
            self.include_trial=0
        else:
           self.end_date=self.return_time() + self.start_date 
        self.save()
        
    def is_active(self):
        if self.end_date<timezone.now():
            return False
        return True

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        new_profile=profile.objects.create(user=instance)
        new_profile.save()
        sessions = Session.objects.all()
        for session in sessions:
            decoded_session=session.get_decoded()
            if 'goals' in decoded_session.keys():
                goals_session=decoded_session
        goals = goals_session['goals']
        for thegoal in goals: 
            from goals.models import goal
            new_goal = goal.objects.create(
                title=thegoal['title'],
                description=thegoal['description'],
                start_date=thegoal['start_date'],
                end_date=thegoal['end_date'],
                owner=new_profile
            )
            new_goal.save()
            for thetask in thegoal['tasks']:
                from goals.models import task
                new_task = task.objects.create(
                    content=thetask['content'],
                    done=thetask['done'],
                    goal=new_goal
                )
                new_task.save()

        
from django.contrib import admin
from .models import price, profile, subscription, service

class priceInline(admin.TabularInline):
    model = price

class ServiceAdmin(admin.ModelAdmin):
    inlines = (priceInline,)

admin.site.register(profile)
admin.site.register(subscription)
admin.site.register(service,ServiceAdmin)



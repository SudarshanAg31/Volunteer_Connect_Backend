from django.contrib import admin
from .models import User, Opportunity, Application

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role', 'phone')
    search_fields = ('name', 'email')

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'ngo_name', 'category', 'location', 'date')
    search_fields = ('title', 'ngo_name', 'description')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'opportunity', 'status', 'applied_date')
    search_fields = ('user__name', 'opportunity__title')
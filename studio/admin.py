from django.contrib import admin
from .models import FitnessClass, Booking

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor', 'datetime', 'total_slots', 'available_slots', 'is_available']
    list_filter = ['name', 'instructor', 'datetime']
    search_fields = ['name', 'instructor']
    ordering = ['datetime']
    
    def is_available(self, obj):
        return obj.is_available()
    is_available.boolean = True
    is_available.short_description = 'Available'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_email', 'fitness_class', 'booked_at', 'is_cancelled']
    list_filter = ['fitness_class__name', 'booked_at', 'is_cancelled']
    search_fields = ['client_name', 'client_email', 'fitness_class__name']
    ordering = ['-booked_at']
    readonly_fields = ['booked_at']
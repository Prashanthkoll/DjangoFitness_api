from django.db import models
from django.core.validators import EmailValidator, MinValueValidator
from django.utils import timezone
import pytz

class FitnessClass(models.Model):
    CLASS_TYPES = [
        ('YOGA', 'Yoga'),
        ('ZUMBA', 'Zumba'),
        ('HIIT', 'HIIT'),
    ]
    
    name = models.CharField(max_length=100, choices=CLASS_TYPES)
    instructor = models.CharField(max_length=100)
    datetime = models.DateTimeField()  # Keep your field name
    total_slots = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    available_slots = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['datetime']
        verbose_name = "Fitness Class"
        verbose_name_plural = "Fitness Classes"
        
    def __str__(self):
        return f"{self.name} - {self.instructor} ({self.datetime})"
    
    def is_available(self):
        """Check if class is available for booking"""
        return self.available_slots > 0 and self.datetime > timezone.now()
    
    def is_past_class(self):
        """Check if class is in the past"""
        return self.datetime <= timezone.now()
    
    def get_local_datetime(self):
        """Get datetime in IST timezone for display"""
        ist = pytz.timezone('Asia/Kolkata')
        return self.datetime.astimezone(ist)
    
    def save(self, *args, **kwargs):
        # Ensure available_slots doesn't exceed total_slots
        if self.available_slots > self.total_slots:
            self.available_slots = self.total_slots
        super().save(*args, **kwargs)

class Booking(models.Model):
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(validators=[EmailValidator()])
    booked_at = models.DateTimeField(default=timezone.now)
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-booked_at']
        # Prevent duplicate active bookings for same user and class
        unique_together = ['fitness_class', 'client_email']
        
    def __str__(self):
        return f"{self.client_name} - {self.fitness_class.name}"
    
    def get_local_booked_time(self):
        """Get booking time in IST timezone for display"""
        ist = pytz.timezone('Asia/Kolkata')
        return self.booked_at.astimezone(ist)
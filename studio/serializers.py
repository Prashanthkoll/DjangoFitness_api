from rest_framework import serializers
from .models import FitnessClass, Booking
from django.core.validators import RegexValidator
from django.utils import timezone

class FitnessClassSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()
    local_datetime = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'instructor', 'datetime', 'local_datetime', 
                 'total_slots', 'available_slots', 'is_available']
        
    def get_is_available(self, obj):
        return obj.is_available()
    
    def get_local_datetime(self, obj):
        return obj.get_local_datetime().strftime('%Y-%m-%d %H:%M:%S IST')

class BookingSerializer(serializers.ModelSerializer):
    fitness_class = FitnessClassSerializer(read_only=True)
    local_booked_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'fitness_class', 'client_name', 'client_email', 
                 'booked_at', 'local_booked_time', 'is_cancelled']
        read_only_fields = ['booked_at']
    
    def get_local_booked_time(self, obj):
        return obj.get_local_booked_time().strftime('%Y-%m-%d %H:%M:%S IST')

class BookingInputSerializer(serializers.Serializer):
    class_id = serializers.IntegerField(required=True)
    client_name = serializers.CharField(
        required=True,
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z \.]+$',
                message="Name must contain only letters, spaces, and dots"
            )
        ]
    )
    client_email = serializers.EmailField(required=True)
    
    def validate_class_id(self, value):
        """Validate class exists and is bookable"""
        try:
            fitness_class = FitnessClass.objects.get(id=value)
            
            if fitness_class.is_past_class():
                raise serializers.ValidationError("Cannot book past classes.")
            
            if not fitness_class.is_available():
                raise serializers.ValidationError("No available slots for this class.")
                
            return value
            
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Class does not exist.")
    
    def validate(self, data):
        """Check for duplicate bookings"""
        try:
            fitness_class = FitnessClass.objects.get(id=data['class_id'])
            existing_booking = Booking.objects.filter(
                fitness_class=fitness_class,
                client_email=data['client_email'],
                is_cancelled=False
            ).exists()
            
            if existing_booking:
                raise serializers.ValidationError({
                    'non_field_errors': ['You have already booked this class.']
                })
                
        except FitnessClass.DoesNotExist:
            pass  # Will be caught by validate_class_id
            
        return data
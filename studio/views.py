from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.timezone import localtime
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer, BookingInputSerializer
import logging
logger = logging.getLogger('studio')

# ====================== API VIEWS ======================

@api_view(['GET'])
def get_classes(request):
    """Get all upcoming fitness classes"""
    try:
        # Filter for upcoming classes only
        classes = FitnessClass.objects.filter(datetime__gt=timezone.now())
        serializer = FitnessClassSerializer(classes, many=True)
        
        logger.info(f"Retrieved {len(classes)} upcoming classes")
        
        # Fixed response format - was returning serializer.data twice
        return Response({
            'status': 'success',
            'data': serializer.data,
            'count': len(classes)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving classes: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to retrieve classes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def book_class(request):
    """Book a fitness class with proper validation and race condition protection"""
    
    # Validate input data
    input_serializer = BookingInputSerializer(data=request.data)
    if not input_serializer.is_valid():
        logger.warning(f"Invalid booking data: {input_serializer.errors}")
        return Response({
            'status': 'error',
            'message': 'Invalid data provided',
            'errors': input_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    data = input_serializer.validated_data

    try:
        # Use database transaction to prevent race conditions
        with transaction.atomic():
            # Lock the fitness class row for update
            fitness_class = FitnessClass.objects.select_for_update().get(id=data['class_id'])
            
            # Double-check availability after acquiring lock
            if not fitness_class.is_available():
                if fitness_class.is_past_class():
                    logger.warning(f"Attempt to book past class: {fitness_class.id}")
                    return Response({
                        'status': 'error',
                        'message': 'Cannot book past classes'
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    logger.warning(f"No slots available for class: {fitness_class.id}")
                    return Response({
                        'status': 'error',
                        'message': 'No slots available'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Check for existing booking (double-check after lock)
            existing_booking = Booking.objects.filter(
                fitness_class=fitness_class,
                client_email=data['client_email'],
                is_cancelled=False
            ).exists()
            
            if existing_booking:
                logger.warning(f"Duplicate booking attempt: {data['client_name']} ({data['client_email']}) for class {fitness_class.id}")
                return Response({
                    'status': 'error',
                    'message': 'You have already booked this class'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create booking
            booking = Booking.objects.create(
                fitness_class=fitness_class,
                client_name=data['client_name'],
                client_email=data['client_email']
            )

        

            logger.info(f"Booking created: {booking.client_name} ({booking.client_email}) for {fitness_class.name}")
            
            # Return booking details
            booking_serializer = BookingSerializer(booking)
            return Response({
                'status': 'success',
                'message': 'Booking created successfully',
                'data': booking_serializer.data
            }, status=status.HTTP_201_CREATED)

    except FitnessClass.DoesNotExist:
        logger.error(f"Invalid fitness class ID: {data['class_id']}")
        return Response({
            'status': 'error',
            'message': 'Invalid class ID'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Unexpected error during booking: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to create booking'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_bookings(request):
    """Get all bookings for a specific email address"""
    try:
        email = request.query_params.get('email')
        if not email:
            return Response({
                'status': 'error',
                'message': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get active bookings only
        bookings = Booking.objects.filter(
            client_email=email,
            is_cancelled=False
        ).select_related('fitness_class')
        
        serializer = BookingSerializer(bookings, many=True)
        
        logger.info(f"Retrieved {len(bookings)} bookings for {email}")
        return Response({
            'status': 'success',
            'data': serializer.data,
            'count': len(bookings)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving bookings: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Failed to retrieve bookings'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ====================== TEMPLATE VIEWS ======================

def home(request):
    """Home page showing upcoming classes"""
    current_time = timezone.now()
    classes = FitnessClass.objects.filter(datetime__gte=current_time).order_by('id')
    return render(request, 'home.html', {'data': classes})

def book_class_page(request):
    """Booking page with form handling"""
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        name = request.POST.get('client_name')
        email = request.POST.get('client_email')

        # Validate required fields
        if not all([class_id, name, email]):
            return render(request, 'book.html', {
                'error': 'All fields are required',
                'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())
            })

        try:
            with transaction.atomic():
                fitness_class = FitnessClass.objects.select_for_update().get(id=class_id)
                
                # Check if class is in the past
                if fitness_class.is_past_class():
                    return render(request, 'book.html', {
                        'error': 'Cannot book past classes',
                        'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())
                    })
                
                # Check available slots
                if fitness_class.available_slots <= 0:
                    return render(request, 'book.html', {
                        'error': 'No slots available for this class',
                        'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())
                    })
                
                # Check for existing booking
                existing_booking = Booking.objects.filter(
                    fitness_class=fitness_class,
                    client_email=email,
                    is_cancelled=False
                ).exists()
                
                if existing_booking:
                    return render(request, 'book.html', {
                        'error': 'You have already booked this class',
                        'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())
                    })
                
                # Create booking
                booking = Booking.objects.create(
                    fitness_class=fitness_class,
                    client_name=name,
                    client_email=email
                )
                
                
                logger.info(f"Web booking created: {name} ({email}) for {fitness_class.name}")
                return render(request, 'book.html', {
                    'message': 'Booking successful!',
                    'booking': booking,
                    'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())
                })
        
        except FitnessClass.DoesNotExist:
            return render(request, 'book.html', {
                'error': 'Invalid class selected',
                'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())
            })
        except Exception as e:
            logger.error(f"Web booking error: {str(e)}")
            return render(request, 'book.html', {'error': 'Booking failed. Please try again.',
                                                 'classes': FitnessClass.objects.filter(datetime__gte=timezone.now())})
    
    # GET request - show booking form
    classes = FitnessClass.objects.filter(datetime__gte=timezone.now()).order_by('id')
    return render(request, 'book.html', {'classes': classes})

def view_bookings_page(request):
    """View bookings page"""
    email = request.GET.get('email')
    bookings = None
    message = None
    
    if email:
        bookings = Booking.objects.filter(client_email=email,is_cancelled=False).select_related('fitness_class').order_by('-booked_at')
        
        if not bookings.exists():
            message = 'No bookings found for this email.'
    
    return render(request, 'viewbook.html', {'bookings': bookings,'message': message,'email': email})

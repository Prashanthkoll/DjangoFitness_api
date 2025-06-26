from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import transaction
import json

from .models import FitnessClass, Booking

class FitnessClassModelTest(TestCase):
    def setUp(self):
        self.future_time = timezone.now() + timedelta(days=1)
        self.past_time = timezone.now() - timedelta(days=1)
        
    def test_create_fitness_class(self):
        fitness_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=self.future_time,
            total_slots=10,
            available_slots=10
        )
        self.assertEqual(fitness_class.name, 'YOGA')
        self.assertTrue(fitness_class.is_available())
        
    def test_is_available_future_class_with_slots(self):
        fitness_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=self.future_time,
            total_slots=10,
            available_slots=5
        )
        self.assertTrue(fitness_class.is_available())
        
    def test_is_not_available_past_class(self):
        fitness_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=self.past_time,
            total_slots=10,
            available_slots=5
        )
        self.assertFalse(fitness_class.is_available())
        self.assertTrue(fitness_class.is_past_class())
        
    def test_is_not_available_no_slots(self):
        fitness_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=self.future_time,
            total_slots=10,
            available_slots=0
        )
        self.assertFalse(fitness_class.is_available())
        
    def test_save_method_limits_available_slots(self):
        fitness_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=self.future_time,
            total_slots=10,
            available_slots=15  # More than total
        )
        self.assertEqual(fitness_class.available_slots, 10)

class BookingModelTest(TestCase):
    def setUp(self):
        self.fitness_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=timezone.now() + timedelta(days=1),
            total_slots=10,
            available_slots=10
        )
        
    def test_create_booking(self):
        booking = Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name='John Doe',
            client_email='john@example.com'
        )
        self.assertEqual(booking.client_name, 'John Doe')
        self.assertEqual(booking.fitness_class, self.fitness_class)
        
    def test_unique_together_constraint(self):
        # Create first booking
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name='John Doe',
            client_email='john@example.com'
        )
        
        # Try to create duplicate booking - should raise IntegrityError
        with self.assertRaises(Exception):
            Booking.objects.create(
                fitness_class=self.fitness_class,
                client_name='John Doe Again',
                client_email='john@example.com'
            )

class APIEndpointTest(APITestCase):
    def setUp(self):
        self.future_time = timezone.now() + timedelta(days=1)
        self.past_time = timezone.now() - timedelta(days=1)
        
        # Create test classes
        self.available_class = FitnessClass.objects.create(
            name='YOGA',
            instructor='Test Instructor',
            datetime=self.future_time,
            total_slots=10,
            available_slots=5
        )
        
        self.full_class = FitnessClass.objects.create(
            name='ZUMBA',
            instructor='Another Instructor',
            datetime=self.future_time + timedelta(hours=1),
            total_slots=10,
            available_slots=0
        )
        
        self.past_class = FitnessClass.objects.create(
            name='HIIT',
            instructor='Past Instructor',
            datetime=self.past_time,
            total_slots=20,
            available_slots=0
        )
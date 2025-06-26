from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking

@receiver(post_save, sender=Booking)
def update_slots_on_booking_create(sender, instance, created, **kwargs):
    if created:
        fitness_class = instance.fitness_class
        if fitness_class.available_slots > 0:
            fitness_class.available_slots -= 1
            fitness_class.save()

@receiver(post_delete, sender=Booking)
def update_slots_on_booking_delete(sender, instance, **kwargs):
    fitness_class = instance.fitness_class
    if fitness_class.available_slots < fitness_class.total_slots:
        fitness_class.available_slots += 1
        fitness_class.save()

from django.urls import path
from . import views

# API URLs
api_urlpatterns = [
    path('classes/', views.get_classes, name='api_get_classes'),
    path('book/', views.book_class, name='api_book_class'),
    path('bookings/', views.get_bookings, name='api_get_bookings'),
]

# Template URLs
template_urlpatterns = [
    path('', views.home, name='home'),
    path('book-class/', views.book_class_page, name='book_class_page'),
    path('view-bookings/', views.view_bookings_page, name='view_bookings_page'),
]

urlpatterns = api_urlpatterns + template_urlpatterns
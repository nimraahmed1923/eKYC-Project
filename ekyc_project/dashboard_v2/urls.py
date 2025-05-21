from django.urls import path
from .views import dashboard_view, login_view, logout_view, home_view

urlpatterns = [
    path('', login_view, name='login'),             # Login view as homepage
    path('login/', login_view, name='login'),       # Explicit login path
    path('logout/', logout_view, name='logout'),    # Logout path
    path('dashboard/', dashboard_view, name='dashboard'),# Correct dashboard view
    path('home/', home_view, name='home'),          # Optional home page
]
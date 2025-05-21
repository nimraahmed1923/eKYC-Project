from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from dashboard_v2.models import EkycData  # Use your actual model

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard_v2/login.html', {'form': form})


# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')


# Dashboard view with search functionality
@login_required
def dashboard_view(request):
    query = request.GET.get('q', '').strip()

    if query:
        recent_entries = EkycData.objects.filter(
            Q(name__icontains=query) |
            Q(aadhaar_number__icontains=query) |
            Q(pan_number__icontains=query) |
            Q(passport_number__icontains=query)
        ).order_by('-timestamp')[:100]
    else:
        recent_entries = EkycData.objects.order_by('-timestamp')[:100]

    context = {
        'total_records': EkycData.objects.count(),
        'aadhaar_count': EkycData.objects.exclude(aadhaar_number__isnull=True).exclude(aadhaar_number__exact='').count(),
        'pan_count': EkycData.objects.exclude(pan_number__isnull=True).exclude(pan_number__exact='').count(),
        'passport_count': EkycData.objects.exclude(passport_number__isnull=True).exclude(passport_number__exact='').count(),
        'recent_entries': recent_entries,
        'query': query,
    }

    return render(request, 'dashboard_v2/dashboard.html', context)


# Optional home view
def home_view(request):
    return render(request, "dashboard_v2/home.html")